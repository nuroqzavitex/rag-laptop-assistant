from pydantic import BaseModel, Field, field_validator

class Specs(BaseModel):
  cpu: str = ''
  ram: str = ''
  screen: str = ''
  gpu: str = ''
  storage: str = ''

class Product(BaseModel):
  id: str
  name: str
  brand: str
  price: float
  currency: str = "VNĐ"
  category: str
  specs: Specs
  stock: int = 0
  image_url: str = ''
  product_url: str = ''
  description: str = ''

  @field_validator('price')
  @classmethod
  def price_must_be_positive(cls, value: str) -> float:
    if value < 0:
      raise ValueError('Giá không được âm')
    return value
  
  @field_validator('stock')
  @classmethod
  def stock_non_negative(cls, value: int)->int:
    return max(0, value)
  
  @property
  def price_range(self) -> str:
    if self.price < 10_000_000:
      return 'duoi_10tr'
    elif self.price < 15_000_000:
      return '10_15tr'
    elif self.price < 20_000_000:
      return '15_20tr'
    elif self.price < 30_000_000:
      return '20_30tr'
    elif self.price < 40_000_000:
      return '30_40tr'
    else:
      return 'tren_40tr'
    
  @property
  def is_in_stock(self) -> bool:
    return self.stock > 0 
    
    
