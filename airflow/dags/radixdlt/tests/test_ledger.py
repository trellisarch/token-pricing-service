from decimal import Decimal
from unittest.mock import patch, MagicMock, call

import pytest

from radixdlt.lib.ledger import get_pool_price, get_ociswap_price


# ---------------------------------------------------------------------------
# get_pool_price: base/quote normalization
# ---------------------------------------------------------------------------


@patch("radixdlt.lib.ledger.get_c9_price")
def test_get_pool_price_c9_xrd_base(mock_c9):
    """When XRD is the base token, raw price is XRD per token — returned as-is."""
    mock_c9.return_value = Decimal("40988.48")
    result = get_pool_price("component_abc", "c9", 100, base="XRD", quote="FLOOP")
    assert result == Decimal("40988.48")
    mock_c9.assert_called_once_with("component_abc", 100)


@patch("radixdlt.lib.ledger.get_c9_price")
def test_get_pool_price_c9_xrd_quote(mock_c9):
    """When XRD is the quote token, raw price is tokens per XRD — return reciprocal."""
    mock_c9.return_value = Decimal("0.000024")
    result = get_pool_price("component_abc", "c9", 100, base="FLOOP", quote="XRD")
    expected = Decimal(1) / Decimal("0.000024")
    assert result == expected
    mock_c9.assert_called_once_with("component_abc", 100)


@patch("radixdlt.lib.ledger.get_ociswap_price")
def test_get_pool_price_ociswap_xrd_base(mock_oci):
    """Ociswap pool with XRD as base — raw price returned as-is."""
    mock_oci.return_value = Decimal("41076.74")
    result = get_pool_price("component_xyz", "ociswap", 100, base="XRD", quote="FLOOP")
    assert result == Decimal("41076.74")
    mock_oci.assert_called_once_with("component_xyz", 100)


@patch("radixdlt.lib.ledger.get_ociswap_price")
def test_get_pool_price_ociswap_xrd_quote(mock_oci):
    """Ociswap pool with XRD as quote — return reciprocal."""
    mock_oci.return_value = Decimal("0.000024")
    result = get_pool_price("component_xyz", "ociswap", 100, base="FLOOP", quote="XRD")
    expected = Decimal(1) / Decimal("0.000024")
    assert result == expected


@patch("radixdlt.lib.ledger.get_c9_price")
def test_xrd_base_and_quote_give_same_xrd_per_token(mock_c9):
    """A pool with XRD as base returning N should give the same result as
    a pool with XRD as quote returning 1/N."""
    xrd_per_token = Decimal("40988.48")

    mock_c9.return_value = xrd_per_token
    result_base = get_pool_price("pool_a", "c9", 100, base="XRD", quote="FLOOP")

    mock_c9.return_value = Decimal(1) / xrd_per_token
    result_quote = get_pool_price("pool_b", "c9", 100, base="FLOOP", quote="XRD")

    assert abs(result_base - result_quote) < Decimal("0.01")


# ---------------------------------------------------------------------------
# get_ociswap_price: basic pool vs precision pool response parsing
# ---------------------------------------------------------------------------


@patch("radixdlt.lib.ledger.preview_transaction")
def test_ociswap_basic_pool_response(mock_preview):
    """Basic/flex pool returns Enum with fields[0].value."""
    mock_preview.return_value = {
        "receipt": {
            "output": [
                {
                    "programmatic_json": {
                        "kind": "Enum",
                        "variant_id": "1",
                        "fields": [
                            {
                                "kind": "PreciseDecimal",
                                "value": "0.838326782386490122079582128141712368",
                            }
                        ],
                    }
                }
            ]
        }
    }
    result = get_ociswap_price("component_basic", 100)
    expected = Decimal("0.838326782386490122079582128141712368") ** 2
    assert result == expected


@patch("radixdlt.lib.ledger.preview_transaction")
def test_ociswap_precision_pool_response(mock_preview):
    """Precision pool returns PreciseDecimal directly at top level (no fields)."""
    mock_preview.return_value = {
        "receipt": {
            "output": [
                {
                    "programmatic_json": {
                        "kind": "PreciseDecimal",
                        "value": "0.120795072475036851862679975083605369",
                    }
                }
            ]
        }
    }
    result = get_ociswap_price("component_precision", 100)
    expected = Decimal("0.120795072475036851862679975083605369") ** 2
    assert result == expected


# ---------------------------------------------------------------------------
# LedgerPriceFetcher.fetch_and_save_prices: full integration
# ---------------------------------------------------------------------------

MOCK_TOKENS = {
    "XRD": {
        "resource_address": "resource_xrd",
        "pools": [],
    },
    "FLOOP": {
        "resource_address": "resource_floop",
        "pools": [
            {
                "component": "comp_c9_floop",
                "dex": "c9",
                "base": "XRD",
                "quote": "FLOOP",
            },
            {
                "component": "comp_oci_floop",
                "dex": "ociswap",
                "base": "XRD",
                "quote": "FLOOP",
            },
        ],
    },
    "hUSDC": {
        "resource_address": "resource_husdc",
        "pools": [
            {
                "component": "comp_c9_husdc",
                "dex": "c9",
                "base": "XRD",
                "quote": "hUSDC",
            },
        ],
    },
}


@patch("radixdlt.models.ledger_prices.token_price.get_session")
@patch("radixdlt.models.ledger_prices.token_price.get_pool_price")
@patch("radixdlt.models.ledger_prices.token_price.get_current_epoch")
def test_fetch_and_save_prices_usd_conversion(
    mock_epoch, mock_pool_price, mock_session
):
    """Verify USD conversion: usd_price = xrd_per_token * husdc_per_xrd."""
    from radixdlt.models.ledger_prices.token_price import LedgerPriceFetcher

    mock_epoch.return_value = 100
    session = MagicMock()
    mock_session.return_value = session

    husdc_per_xrd = Decimal("0.00185")
    floop_c9_xrd = Decimal("40988")
    floop_oci_xrd = Decimal("41076")

    def pool_price_side_effect(component, dex, epoch, base, quote):
        if component == "comp_c9_husdc":
            return husdc_per_xrd
        if component == "comp_c9_floop":
            return floop_c9_xrd
        if component == "comp_oci_floop":
            return floop_oci_xrd

    mock_pool_price.side_effect = pool_price_side_effect

    LedgerPriceFetcher.fetch_and_save_prices(MOCK_TOKENS)

    # Collect all session.add calls to check saved prices
    saved = {}
    for c in session.add.call_args_list:
        obj = c[0][0]
        saved[obj.resource_address] = obj.usd_price

    # XRD price = husdc_per_xrd
    assert saved["resource_xrd"] == float(husdc_per_xrd)

    # hUSDC price = 1.0
    assert saved["resource_husdc"] == 1.0

    # FLOOP price = average of (c9_xrd * husdc) and (oci_xrd * husdc)
    expected_c9 = floop_c9_xrd * husdc_per_xrd
    expected_oci = floop_oci_xrd * husdc_per_xrd
    expected_avg = float((expected_c9 + expected_oci) / 2)
    assert saved["resource_floop"] == pytest.approx(expected_avg, rel=1e-6)

    session.commit.assert_called_once()
    session.close.assert_called_once()


@patch("radixdlt.models.ledger_prices.token_price.get_session")
@patch("radixdlt.models.ledger_prices.token_price.get_pool_price")
@patch("radixdlt.models.ledger_prices.token_price.get_current_epoch")
def test_fetch_and_save_prices_pool_failure_skips_token(
    mock_epoch, mock_pool_price, mock_session
):
    """When all pools fail for a token, that token is skipped but others still saved."""
    from radixdlt.models.ledger_prices.token_price import LedgerPriceFetcher

    mock_epoch.return_value = 100
    session = MagicMock()
    mock_session.return_value = session

    def pool_price_side_effect(component, dex, epoch, base, quote):
        if component == "comp_c9_husdc":
            return Decimal("0.00185")
        # All FLOOP pools fail
        raise Exception("Gateway error")

    mock_pool_price.side_effect = pool_price_side_effect

    LedgerPriceFetcher.fetch_and_save_prices(MOCK_TOKENS)

    saved_addresses = [c[0][0].resource_address for c in session.add.call_args_list]
    # XRD and hUSDC saved, FLOOP skipped
    assert "resource_xrd" in saved_addresses
    assert "resource_husdc" in saved_addresses
    assert "resource_floop" not in saved_addresses

    session.commit.assert_called_once()


@patch("radixdlt.models.ledger_prices.token_price.get_session")
@patch("radixdlt.models.ledger_prices.token_price.get_pool_price")
@patch("radixdlt.models.ledger_prices.token_price.get_current_epoch")
def test_fetch_and_save_prices_partial_pool_failure(
    mock_epoch, mock_pool_price, mock_session
):
    """When one pool fails but another succeeds, uses the successful pool's price."""
    from radixdlt.models.ledger_prices.token_price import LedgerPriceFetcher

    mock_epoch.return_value = 100
    session = MagicMock()
    mock_session.return_value = session

    husdc_per_xrd = Decimal("0.00185")
    floop_c9_xrd = Decimal("40988")

    def pool_price_side_effect(component, dex, epoch, base, quote):
        if component == "comp_c9_husdc":
            return husdc_per_xrd
        if component == "comp_c9_floop":
            return floop_c9_xrd
        if component == "comp_oci_floop":
            raise Exception("Ociswap pool error")

    mock_pool_price.side_effect = pool_price_side_effect

    LedgerPriceFetcher.fetch_and_save_prices(MOCK_TOKENS)

    saved = {}
    for c in session.add.call_args_list:
        obj = c[0][0]
        saved[obj.resource_address] = obj.usd_price

    # FLOOP price from C9 pool only (no average since ociswap failed)
    expected = float(floop_c9_xrd * husdc_per_xrd)
    assert saved["resource_floop"] == pytest.approx(expected, rel=1e-6)


@patch("radixdlt.models.ledger_prices.token_price.get_session")
@patch("radixdlt.models.ledger_prices.token_price.get_pool_price")
@patch("radixdlt.models.ledger_prices.token_price.get_current_epoch")
def test_fetch_and_save_prices_prefers_c9_for_husdc(
    mock_epoch, mock_pool_price, mock_session
):
    """Fetcher picks the C9 pool for the hUSDC rate even if ociswap is listed first."""
    from radixdlt.models.ledger_prices.token_price import LedgerPriceFetcher

    mock_epoch.return_value = 100
    session = MagicMock()
    mock_session.return_value = session

    tokens_oci_first = {
        "XRD": {"resource_address": "resource_xrd", "pools": []},
        "hUSDC": {
            "resource_address": "resource_husdc",
            "pools": [
                {
                    "component": "comp_oci_husdc",
                    "dex": "ociswap",
                    "base": "XRD",
                    "quote": "hUSDC",
                },
                {
                    "component": "comp_c9_husdc",
                    "dex": "c9",
                    "base": "XRD",
                    "quote": "hUSDC",
                },
            ],
        },
    }

    def pool_price_side_effect(component, dex, epoch, base, quote):
        if component == "comp_c9_husdc":
            return Decimal("0.00185")
        if component == "comp_oci_husdc":
            return Decimal("0.00190")

    mock_pool_price.side_effect = pool_price_side_effect

    LedgerPriceFetcher.fetch_and_save_prices(tokens_oci_first)

    saved = {}
    for c in session.add.call_args_list:
        obj = c[0][0]
        saved[obj.resource_address] = obj.usd_price

    # Should use C9 price (0.00185), not ociswap (0.00190)
    assert saved["resource_xrd"] == float(Decimal("0.00185"))


@patch("radixdlt.models.ledger_prices.token_price.get_session")
@patch("radixdlt.models.ledger_prices.token_price.get_pool_price")
@patch("radixdlt.models.ledger_prices.token_price.get_current_epoch")
def test_fetch_and_save_missing_husdc_raises(mock_epoch, mock_pool_price, mock_session):
    """Raises ValueError if hUSDC is not in the tokens config."""
    from radixdlt.models.ledger_prices.token_price import LedgerPriceFetcher

    mock_epoch.return_value = 100
    session = MagicMock()
    mock_session.return_value = session

    tokens_no_husdc = {
        "XRD": {"resource_address": "resource_xrd", "pools": []},
    }

    with pytest.raises(ValueError, match="hUSDC must be in LEDGER_TOKENS"):
        LedgerPriceFetcher.fetch_and_save_prices(tokens_no_husdc)

    session.rollback.assert_called_once()
