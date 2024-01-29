"""add legacy tables

Revision ID: fa409f33202a
Revises: 18e94aa2cc1e
Create Date: 2024-01-25 16:24:39.198082

"""
from csv import DictReader
from datetime import datetime
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from os.path import join, dirname, abspath
import pandas as pd

# revision identifiers, used by Alembic.
revision: str = 'fa409f33202a'
down_revision: Union[str, None] = '18e94aa2cc1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "legacy_exec_overview",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("new_wallet_downloads_ios_android", sa.Integer(), nullable=True),
        sa.Column("cumulative_downloads", sa.Integer(), nullable=True),
        sa.Column("tvl", sa.Integer(), nullable=True),
        sa.Column("total_stake", sa.BigInteger(), nullable=True),
        sa.Column("xrd_price_vs_comp", sa.Integer(), nullable=True),
        sa.Column("weekly_tx_volume", sa.Integer(), nullable=True),                
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_reddit",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("pageviews", sa.Integer(), nullable=True),
        sa.Column("total_subscribers", sa.Integer(), nullable=True),
        sa.Column("uniques_on_average", sa.Integer(), nullable=True),            
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_discord",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("total_users", sa.String(), nullable=True),
        sa.Column("weekly_new_members", sa.Integer(), nullable=True),
        sa.Column("total_messages", sa.String(), nullable=True),     
        sa.Column("dev_weeklyu_new_members", sa.Integer(), nullable=True),     
        sa.Column("dev_total_messages", sa.Integer(), nullable=True),            
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_x",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("followers", sa.Integer(), nullable=True),
        sa.Column("net_new_followers", sa.Integer(), nullable=True),
        sa.Column("unfollow", sa.Integer(), nullable=True),     
        sa.Column("likes", sa.Integer(), nullable=True),            
        sa.Column("retweets", sa.Integer(), nullable=True),            
        sa.Column("replies_comments", sa.Integer(), nullable=True),            
        sa.Column("mentions", sa.Integer(), nullable=True),            
        sa.Column("impressions", sa.Integer(), nullable=True),            
        sa.Column("engament_rate", sa.Integer(), nullable=True),                    
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_youtube",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("total_views", sa.Integer(), nullable=True),
        sa.Column("average_watchtime", sa.Integer(), nullable=True),
        sa.Column("new_subs", sa.Integer(), nullable=True),
        sa.Column("watch_time", sa.Integer(), nullable=True),            
        sa.Column("impressions", sa.Integer(), nullable=True),            
        sa.Column("watch_ratio", sa.Integer(), nullable=True),            
        sa.Column("unique_viewers", sa.Integer(), nullable=True),                           
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_ios_appstore",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("total_downloads", sa.Integer(), nullable=True),
        sa.Column("sessions_p_active_device", sa.Integer(), nullable=True),
        sa.Column("day_1_retention", sa.Integer(), nullable=True),
        sa.Column("avg_retention", sa.Integer(), nullable=True),
        sa.Column("total_ratings", sa.Integer(), nullable=True),            
        sa.Column("average_rating", sa.Integer(), nullable=True),            
        sa.Column("impressions", sa.Integer(), nullable=True),                          
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_playstore",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("store_listing_acquisitions", sa.Integer(), nullable=True),
        sa.Column("daily_active_users", sa.Integer(), nullable=True),
        sa.Column("monthly_active_users", sa.Integer(), nullable=True),            
        sa.Column("installed_audience", sa.Integer(), nullable=True),            
        sa.Column("monthly_returning_users", sa.Integer(), nullable=True),            
        sa.Column("total_ratings", sa.Integer(), nullable=True),            
        sa.Column("average_rating", sa.Integer(), nullable=True),                            
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_telegram",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("total_users", sa.Integer(), nullable=True),
        sa.Column("new_users", sa.Integer(), nullable=True),
        sa.Column("weekly_active_users", sa.Integer(), nullable=True),            
        sa.Column("total_messages", sa.Integer(), nullable=True),
        sa.Column("dev_total_users", sa.Integer(), nullable=True),
        sa.Column("dev_new_users", sa.Integer(), nullable=True),
        sa.Column("dev_weekly_active_users", sa.Integer(), nullable=True),            
        sa.Column("dev_total_messages", sa.Integer(), nullable=True),                         
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_network",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("weekly_tx_volume", sa.Integer(), nullable=True),
        sa.Column("tvl", sa.Integer(), nullable=True),
        sa.Column("total_xrd_staked", sa.Integer(), nullable=True),
        sa.Column("accounts_with_2000_xrd", sa.Integer(), nullable=True),                      
        sa.Column("fees_burned_xrd", sa.Integer(), nullable=True),            
        sa.Column("e_xrd_traded_vol_avg", sa.Integer(), nullable=True),            
        sa.Column("xrd_price_vs_comp", sa.Integer(), nullable=True),          
        sa.Column("users", sa.Integer(), nullable=True),                      
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_ecosystem",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("dei", sa.Integer(), nullable=True),
        sa.Column("how_many_dapps_launch", sa.Integer(), nullable=True),      
        sa.Column("signups_for_dev_program", sa.Integer(), nullable=True),              
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "legacy_website",
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("views_radixdlt_com", sa.Integer(), nullable=True),
        sa.Column("users_radixdlt_com", sa.Integer(), nullable=True),
        sa.Column("new_users_radixdlt_com", sa.Integer(), nullable=True),
        sa.Column("none_1", sa.Integer(), nullable=True),                  
        sa.Column("views_devs_radixdlt_com", sa.Integer(), nullable=True),            
        sa.Column("users_devs_radixdlt_com", sa.Integer(), nullable=True),            
        sa.Column("new_users_devs_radixdlt_com", sa.Integer(), nullable=True),
        sa.Column("none_2", sa.Integer(), nullable=True),                  
        sa.Column("docs_page_views", sa.Integer(), nullable=True),            
        sa.Column("docs_reads", sa.Integer(), nullable=True),   
        sa.Column("devs_page_views", sa.Integer(), nullable=True),       
        sa.Column("devs_active_users", sa.Integer(), nullable=True),                    
        sa.PrimaryKeyConstraint("date"),
    )

    legacy_exec_overview_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_exec_overview.csv")
    pd.read_csv(legacy_exec_overview_path).to_sql('legacy_exec_overview', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_reddit_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_reddit.csv")
    pd.read_csv(legacy_reddit_path).to_sql('legacy_reddit', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_discord_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_discord.csv")
    pd.read_csv(legacy_discord_path).to_sql('legacy_discord', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_x_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_x.csv")
    pd.read_csv(legacy_x_path).to_sql('legacy_x', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_youtube_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_youtube.csv")
    pd.read_csv(legacy_youtube_path).to_sql('legacy_youtube', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_ios_appstore_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_ios_appstore.csv")
    pd.read_csv(legacy_ios_appstore_path).to_sql('legacy_ios_appstore', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_playstore_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_playstore.csv")
    pd.read_csv(legacy_playstore_path).to_sql('legacy_playstore', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_telegram_radix_dlt_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_telegram_radix_dlt.csv")
    pd.read_csv(legacy_telegram_radix_dlt_path).to_sql('legacy_telegram_radix_dlt', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_telegram_radix_dlt_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_telegram_radix_dlt.csv")
    pd.read_csv(legacy_telegram_radix_dlt_path).to_sql('legacy_telegram_radix_dlt', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_network_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_network.csv")
    pd.read_csv(legacy_network_path).to_sql('legacy_network', con=op.get_bind(), if_exists='replace', index=False)
    
    legacy_ecosystem_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_ecosystem.csv")
    pd.read_csv(legacy_ecosystem_path).to_sql('legacy_ecosystem', con=op.get_bind(), if_exists='replace', index=False)

    legacy_website_path = join(dirname(dirname(dirname(abspath(__file__)))),"legacy","legacy_website.csv")
    pd.read_csv(legacy_website_path).to_sql('legacy_website', con=op.get_bind(), if_exists='replace', index=False)
    

def downgrade() -> None:
    op.drop_table("legacy_exec_overview")
    op.drop_table("legacy_reddit")
    op.drop_table("legacy_discord")
    op.drop_table("legacy_x")
    op.drop_table("legacy_youtube")
    op.drop_table("legacy_ios_appstore")
    op.drop_table("legacy_playstore")
    op.drop_table("legacy_telegram_radix_dlt")
    op.drop_table("legacy_network")
    op.drop_table("legacy_ecosystem")
    op.drop_table("legacy_website")

