from decimal import Decimal
from unittest.mock import patch

from radixdlt.lib.ledger import get_pool_price


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

    # Pool where XRD is base: get_price returns 40988.48 (XRD per token)
    mock_c9.return_value = xrd_per_token
    result_base = get_pool_price("pool_a", "c9", 100, base="XRD", quote="FLOOP")

    # Pool where XRD is quote: get_price returns 1/40988.48 (tokens per XRD)
    mock_c9.return_value = Decimal(1) / xrd_per_token
    result_quote = get_pool_price("pool_b", "c9", 100, base="FLOOP", quote="XRD")

    assert abs(result_base - result_quote) < Decimal("0.01")
