from .model import (
    UserSchema, CommentSchema, CategorySchema, ArticleSchema
)
from .frontend import (
    ArticleViewSchema, IndexViewSchema, CategoryArticlesViewSchema
)
from .user import ProfileViewSchema
from .general import (
    LoginManagerSchema, UserInfoSchema, CommentWithUserSchema, ArticleWithAuthorSchema,
    NavbarSchema
)

# shallow schemas
user_serializer = UserSchema()
user_info_serializer = UserInfoSchema()

article_serializer = ArticleSchema()

comment_serializer = CommentSchema()

category_serializer = CategorySchema()

navbar_serializer = NavbarSchema()

login_manager_serializer = LoginManagerSchema()

# "nested" schemas
article_with_author_serializer = ArticleWithAuthorSchema()

comment_with_user_serializer = CommentWithUserSchema()

# View based schemas
frontend_index_view_serializer = IndexViewSchema()
frontend_article_view_serializer = ArticleViewSchema()
frontend_category_articles_serializer = CategoryArticlesViewSchema()
user_profile_view_serializer = ProfileViewSchema()