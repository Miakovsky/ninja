from ninja import NinjaAPI, Schema, Field
from .models import Category, Product, Wishlist, Order, OrderItem, Status
from ninja import UploadedFile, File
from django.shortcuts import get_object_or_404
from typing import List
from django.contrib.auth import authenticate, login, logout
from ninja.errors import HttpError, AuthenticationError
from django.contrib.auth.models import User
from ninja import Query
from typing import Optional

api = NinjaAPI()

############## КАТЕГОРИИ-ПРОДУКТЫ ##############
class CategoryIn(Schema):
    title: str
    slug: str

class ProductIn(Schema):
    title: str
    slug: str
    category: str
    description: str
    price: float 

@api.post("/categories")
def create_category(request, payload: CategoryIn):
    category = Category.objects.create(**payload.dict())
    return {"id": category.id}

@api.post("/products")
def create_product(request, payload: ProductIn, image: UploadedFile = File(...)):
    payload_dict = payload.dict()
    category = get_object_or_404(Category, slug=payload_dict.pop('category'))
    product = Product(**payload_dict, category=category)
    product.image.save(image.name, image) # will save model instance as well
    return {"id": product.id}

class CategoryOut(Schema):
    id: int
    title: str
    slug: str

class ProductOut(Schema):
    id: int
    title: str
    slug: str
    category_id: int
    description: str
    price: float 

class ProductFilter(Schema):
    min_price: Optional[float]
    max_price: Optional[float]
    title: Optional[str]
    description: Optional[str]

@api.get("/categories/{category_slug}", response=CategoryOut)
def get_category(request, category_slug: str):
    category = get_object_or_404(Category, slug=category_slug)
    return category

@api.get("/products/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product

@api.get("/categories", response=List[CategoryOut])
def list_categories(request):
    qs = Category.objects.all()
    return qs

@api.get("/products", response=List[ProductOut])
def list_product(request,
                min_price: Optional[float] = None,
                max_price: Optional[float] = None,
                title: Optional[str] = None,
                description: Optional[str] = None):
    qs = Product.objects.all()

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)
    if title:
        products = products.filter(title__icontains=title)
    if description:
        products = products.filter(description__icontains=description)
    return qs

@api.put("/products/{product_id}")
def update_product(request, product_id: int, payload: ProductIn):
    product = get_object_or_404(Product, id=product_id)
    for attr, value in payload.dict().items():
        if attr == 'category':
            category = get_object_or_404(Category, slug=value)
            setattr(product, attr, category)
        else:
            setattr(product, attr, value)
    product.save()
    return {"success": True}

@api.delete("/categories/{category_slug}")
def delete_category(request, category_slug: str):
    category = get_object_or_404(Category, slug=category_slug)
    category.delete()
    return {"success": True}

@api.delete("/products/{product_id}")
def delete_product(request, product_id: str):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}

############## АУТЕНТИФИКАЦИЯ ##############
class UserAuthentication(Schema):
    username: str
    password: str


class UserRegistration(Schema):
    username: str
    email: str
    password1: str
    password2: str
    

class UserOut(Schema):
    username: str
    email: str

@api.get('/user')
def get_user(request):
    if not request.user.is_authenticated:
        raise HttpError(401, 'Вы не авторизованы!')
    return request.user


@api.post('/login')
def login_user(request, payload: UserAuthentication):
    user = authenticate(username = payload.username, password = payload.password)
    if user is not None:
        login(request, user)
        return { 'Успешно!': 'Добро пожаловать!', 'Логин пользователя': user.username }
    raise AuthenticationError('Ошибка авторизации!')


@api.post('/registration')
def registration_user(request, payload: UserRegistration):
    if User.objects.filter(username = payload.username).exists():
        raise HttpError(400, 'Пользователь с таким именем уже существует!')
    
    user = User.objects.create_user(
        username = payload.username,
        email = payload.email,
        password = payload.password1
    )
    login(request, user)
    
    return { 'Успешно!': 'Авторизация прошла успешно!', 'Логин пользователя': user.username }


@api.post('/logout', auth = None)
def logout_user(request):
    logout(request)
    return {'Успешно!': 'Вы вышли из аккаунта!'}


@api.get('/users', response = List[UserOut])
def users(request):
    get_user(request)
    
    if request.user.has_perm('auth.view_user'):
        return User.objects.all()
    else:
        raise HttpError(403, 'У вас недостаточно прав для просмотра этой информации!')
    
############## ВИШЛИСТЫ И ЗАКАЗЫ ##############
class WishlistIn(Schema):
    user: int
    product: int
    quantity: int


class WishlistOut(Schema):
    product: ProductOut
    quantity: int


class StatusOut(Schema):
    name: str


class OrderOut(Schema):
    status: StatusOut
    total: float


class OrderIn(Schema):
    user: int
    status: int
    total: float


class OrderItemOut(Schema):
    order: OrderOut
    product: ProductOut
    cost: float
    quantity: int


class OrderItemIn(Schema):
    order: int
    product: int
    cost: float
    quantity: int

@api.get('/wishlist/{user_id}/', response = List[WishlistOut])
def get_wishlist(request, user_id: int):
    '''user = get_object_or_404(User, id = request.user.id)'''
    user = get_object_or_404(User, id = user_id)
    wishlist = Wishlist.objects.filter(user = user)
    return wishlist


@api.post('/wishlist', response = WishlistOut)
def create_wishlist(request, payload: WishlistIn):
    payload_dict = payload.dict()
    '''user = get_object_or_404(User, id = request.user.id)'''
    user = get_object_or_404(User, id = payload_dict.pop('user'))
    product = get_object_or_404(Product, id = payload_dict.pop('product'))

    if Wishlist.objects.filter(user = user, product = product).exists():
        wishlist = get_object_or_404(Wishlist, user = user, product = product)
        wishlist.quantity = payload_dict.pop('quantity')
    else:
        wishlist = Wishlist(**payload_dict, user = user, product = product)    

    wishlist.save()
    return wishlist


@api.put('/wishlist_add', response = WishlistOut)
def add_to_wishlist(request, wishlist_id: int):
    wishlist = get_object_or_404(Wishlist, id = wishlist_id)
    wishlist.quantity += 1
    wishlist.save()
    return wishlist


@api.put('/wishlist_remove', response = WishlistOut)
def remove_from_wishlist(request, wishlist_id: int):
    wishlist = get_object_or_404(Wishlist, id = wishlist_id)
    wishlist.quantity -= 1

    if wishlist.quantity == 0:
        wishlist.delete()
    else:
        wishlist.save()

    return wishlist


@api.get('/orders', response = List[OrderItemOut])
def list_orders(request):
    return OrderItem.objects.all()


@api.get('/order/{user_id}/', response = List[OrderItemOut])
def get_user_orders(request, user_id: int):
    '''user = get_object_or_404(User, id = request.user.id)'''
    user = get_object_or_404(User, id = user_id)
    order = get_object_or_404(Order, user = user)
    order_items = OrderItem.objects.filter(order = order)
    return order_items


@api.post('/order', response = OrderOut)
def create_order(request, wishlists: List[int]):
    '''Получаю список id листов желаний, которые будут включены в заказ'''
    status = get_object_or_404(Status, id = 1)
    wishlist = get_object_or_404(Wishlist, id = wishlists[0])
    order = Order(user = wishlist.user, status = status, total = 0)   
    order.save()
    '''Прохожусь по всем id и собираю их в элементы заказа'''
    for item in wishlists:
        wishlist = get_object_or_404(Wishlist, id = item)
        OrderItem.objects.create(
            order = order,
            product = wishlist.product,
            quantity = wishlist.quantity,
            cost = wishlist.product.price * wishlist.quantity
        )
    
    order.total += order.get_total_amount()  
    order.save()

    return order


@api.put('/change_status', response = OrderOut)
def change_status(request, order_id: int, status_id: int):
    order = get_object_or_404(Order, id = order_id)
    status = get_object_or_404(Status, id = status_id)
    order.status = status
    order.save()
    return order