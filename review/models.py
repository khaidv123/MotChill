"""
Module: review.py
Description: Contains the Review model for user reviews related to movies.
"""

from django.db import models
from django.contrib.auth.models import User
from movie.models import Movie

class Review(models.Model):
    """
    Represents a review related to a movie in the application.

    Attributes:
    - user (ForeignKey[User]): Foreign key relationship with the User model from Django's auth system.
    - movie (ForeignKey[Movie]): Foreign key relationship with the Movie model.
    - rating (float): The rating given for the movie.
    - comment (str): The comment or review content.
    # Add other review-related fields
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField(blank=False, null=False, default=0)
    comment = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

'''
File `models.py` trong thư mục `/review` định nghĩa mô hình (model) `Review`, được sử dụng để lưu trữ các đánh giá của người dùng về các bộ phim trong ứng dụng. Đây là một phần quan trọng của ứng dụng, cho phép người dùng tương tác và đánh giá các bộ phim. Hãy cùng giải thích chi tiết từng dòng code và cách nó hoạt động:

### **Phần mô tả**

```python
"""
Module: review.py
Description: Contains the Review model for user reviews related to movies.
"""
```
- Đây là phần bình luận ở đầu file để mô tả nội dung của module. Nó chỉ rõ rằng module này chứa model `Review` dùng để quản lý các đánh giá của người dùng liên quan đến phim.

### **Imports**

```python
from django.db import models
from django.contrib.auth.models import User
from movie.models import Movie
```
- **`django.db import models`**: Import module `models` của Django, cung cấp các lớp và phương thức để định nghĩa các model trong Django.
- **`django.contrib.auth.models import User`**: Import model `User` từ hệ thống xác thực của Django. Đây là model mặc định của Django dùng để quản lý người dùng.
- **`movie.models import Movie`**: Import model `Movie` từ ứng dụng `movie`. Model này đại diện cho các bộ phim trong ứng dụng và sẽ được liên kết với `Review` qua mối quan hệ khóa ngoại (Foreign Key).

### **Định nghĩa model `Review`**

```python
class Review(models.Model):
    """
    Represents a review related to a movie in the application.

    Attributes:
    - user (ForeignKey[User]): Foreign key relationship with the User model from Django's auth system.
    - movie (ForeignKey[Movie]): Foreign key relationship with the Movie model.
    - rating (float): The rating given for the movie.
    - comment (str): The comment or review content.
    # Add other review-related fields
    """
```
- **`class Review(models.Model):`**: Khởi tạo lớp `Review`, kế thừa từ `models.Model`. Đây là lớp đại diện cho bảng `Review` trong cơ sở dữ liệu.
- **Docstring**: Giải thích các thuộc tính (attributes) của model `Review`, gồm `user`, `movie`, `rating`, và `comment`.

### **Các thuộc tính của `Review`**

```python
user = models.ForeignKey(User, on_delete=models.CASCADE)
```
- **`user`**: Thiết lập mối quan hệ Foreign Key với model `User`. Mỗi review sẽ liên kết với một người dùng cụ thể. 
  - **`on_delete=models.CASCADE`**: Khi người dùng bị xóa, tất cả các review liên quan đến người dùng này cũng sẽ bị xóa theo.

```python
movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
```
- **`movie`**: Thiết lập mối quan hệ Foreign Key với model `Movie`. Mỗi review sẽ liên kết với một bộ phim cụ thể. 
  - **`on_delete=models.CASCADE`**: Khi một bộ phim bị xóa, tất cả các review liên quan đến phim này cũng sẽ bị xóa theo.

```python
rating = models.FloatField(blank=False, null=False, default=0)
```
- **`rating`**: Trường số thực lưu trữ điểm đánh giá của người dùng cho bộ phim. 
  - **`blank=False, null=False`**: Trường này không được để trống.
  - **`default=0`**: Mặc định điểm đánh giá là 0 nếu không có giá trị nào được nhập vào.

```python
comment = models.TextField()
```
- **`comment`**: Trường văn bản lưu trữ nội dung nhận xét của người dùng về bộ phim. Trường này không giới hạn độ dài.

### **Phương thức `__str__`**

```python
def __str__(self):
    return f"{self.user.username} - {self.movie.title}"
```
- **`__str__`**: Phương thức này xác định chuỗi đại diện cho một đối tượng `Review`. Khi bạn in hoặc xem một đối tượng `Review` trong admin hoặc shell của Django, nó sẽ hiển thị dưới dạng "username - movie title". Điều này giúp dễ dàng nhận diện các review khi làm việc với chúng.

### **Tác động của model `Review` đến các thành phần khác**

1. **Cơ sở dữ liệu**: 
   - Model `Review` sẽ được dịch thành một bảng trong cơ sở dữ liệu với các cột tương ứng với các thuộc tính (`user`, `movie`, `rating`, `comment`).
   - Các mối quan hệ khóa ngoại giúp liên kết bảng `Review` với bảng `User` và `Movie`, cho phép truy vấn và quản lý dữ liệu liên quan dễ dàng.

2. **Admin Panel**: 
   - Khi bạn đăng ký model `Review` với admin của Django, bạn có thể quản lý các đánh giá trực tiếp từ admin panel. 
   - Các review có thể được tạo, sửa, và xóa thông qua giao diện quản trị này.

3. **Giao diện người dùng**: 
   - Người dùng sẽ có thể để lại đánh giá và xếp hạng phim. Các đánh giá này có thể được hiển thị trên trang chi tiết của từng bộ phim.
   - Các form để người dùng tạo hoặc chỉnh sửa review có thể được tạo tự động bằng cách sử dụng các form của Django, dựa trên model này.

### **Cách tạo và quản lý `Review` trong cơ sở dữ liệu**

- **Tạo một review mới**: Người dùng có thể tạo một review bằng cách điền vào một form trong giao diện web. Khi form được gửi, dữ liệu sẽ được lưu vào bảng `Review` trong cơ sở dữ liệu.
  
- **Quản lý review**: Review có thể được quản lý (tạo, sửa, xóa) thông qua giao diện quản trị của Django hoặc trực tiếp bằng cách sử dụng các API nếu bạn có API trong ứng dụng.
'''