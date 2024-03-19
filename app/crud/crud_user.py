from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_uid(self, db: Session, uid: str = None):
        return db.query(User).filter(User.uid == uid).first()


user = CRUDUser(User)
