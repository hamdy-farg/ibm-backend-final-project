import uuid
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from db import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(32), primary_key=True, nullable=False, default=lambda: uuid.uuid4().hex)
    created_at = db.Column(db.DateTime(timezone=True),default=func.now(),nullable=False )
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def save(self):
        """save the object to the database."""  
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return False
        

    def delete(self):
        """ delete the object from database"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            return False

    def update(self, **kwargs):
        """
        Update specific fields of an object.
        
        Example usage:
            user.update(email_address="new_email@example.com", phone_number="1234567890")
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Automatically update the `updated_at` field
        self.updated_at = func.now()

        # Commit changes to the database
        done =  self.save()
        return done
