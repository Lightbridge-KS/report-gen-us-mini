from typing import Optional, List
from langchain_core.pydantic_v1 import BaseModel, Field


class Organ(BaseModel):
    """Base class for organ-related information"""
    finding: Optional[str] = Field(default=None, description="")

    def __init__(self, **data):
        super().__init__(**data)
        # Dynamically set the description
        cls_nm = self.__class__.__name__
        self.__fields__["finding"].field_info.description = f"Abnormal finding for the {cls_nm}. If findings about {cls_nm} is not provided or {cls_nm} is normal, return `None`."

    class Config:
        # This ensures that the fields are allowed to be inherited and validated correctly.
        allow_population_by_field_name = True
        
class Liver(Organ):
    """Information about Liver finding"""
 

class Kidney(Organ):
    """Information about Kidney finding"""
   
class GallBladder(Organ):
    """Information about GallBladder finding"""
    

class Findings(BaseModel):
    """Extracted information from each organs."""
    # Creates a model so that we can extract multiple entities.
    abnormal_liver: List[Liver]
    abnormal_kidney: List[Kidney]
    abnormal_gallbladder: List[GallBladder]
    
    def to_dict(self):
        return {
            "abnormal_liver": [sub.finding for sub in self.abnormal_liver],
            "abnormal_kidney": [sub.finding for sub in self.abnormal_kidney],
            "abnormal_gallbladder": [sub.finding for sub in self.abnormal_gallbladder],
        }
    


if __name__ == "__main__":
    # Example usage
    liver_instance = Liver()
    kidney_instance = Kidney()
    gallbladder_instance = GallBladder()

    print(liver_instance.__fields__["finding"].field_info.description)  
    print(kidney_instance.__fields__["finding"].field_info.description)  
    print(gallbladder_instance.__fields__["finding"].field_info.description)