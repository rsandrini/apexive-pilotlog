from .base_model import BaseModel


class ImagePic(BaseModel):

    def __str__(self):
        return f"ImagePic {self.guid}"
