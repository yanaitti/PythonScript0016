from sqlalchemy import Column, Integer, String, Boolean
from flaski.database import Base

# テーブル情報 魚マスタ
class FishMaster(Base):
    # テーブル名の設定
    __tablename__ = "fish_master"
    # Column情報の設定
    fish_name       = Column(String, primary_key=True)    # 魚名
    poison          = Column(Integer)                     # 毒の有無(0:無毒 1:有毒)
    poison_part     = Column(String)                      # 毒を含む部位
    wiki_url        = Column(String)                      # WikipediaのURL
    picture_path    = Column(String)                      # 魚画像パス
    copyright_owner = Column(String)                      # 権利情報
    copyright_url   = Column(String)                      # 権利情報URL

    def __init__(self, fish_name=None, poison=None, poison_part=None, wiki_url=None, picture_path=None, copyright_owner=None, copyright_url=None):
        self.fish_name       = fish_name
        self.poison          = poison
        self.poison_part     = poison_part
        self.wiki_url        = wiki_url
        self.picture_path    = picture_path
        self.copyright_owner = copyright_owner
        self.copyright_url   = copyright_url