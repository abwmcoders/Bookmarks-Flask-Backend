from flask  import Blueprint, request, jsonify
import validators
from src.constants.status_code import *
from src.database import db, Bookmark
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from flasgger import swag_from


bookmarks = Blueprint("bookmarks", __name__,url_prefix="/api/v1/bookmarks")


@bookmarks.route("/", methods=['GET', 'POST'])
# @swag_from('./docs/bookmarks/.yaml')
@jwt_required()
def handle_books():
    current_user= get_jwt_identity()
    if request.method == "POST":
        body= request.get_json().get('body', '')
        url= request.get_json().get('url', '')
        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'Url already exists'
            }), HTTP_409_CONFLICT
        bookmark= Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED
    else:
        page= request.args.get("page", 1, type=int)
        per_page= request.args.get("per_page", 5, type=int)
        bookmark_list= Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
        data= []
        for bookmark in bookmark_list.items:
            data.append({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
            })

        meta= {
            "page": bookmark_list.page,
            "pages": bookmark_list.pages,
            "total_count": bookmark_list.total,
            "prev": bookmark_list.prev_num,
            "next_page": bookmark_list.next_num,
            "has_next": bookmark_list.has_next,
            "has_prev": bookmark_list.has_prev,
        }    

        return jsonify({
            'data': data,
            'meta': meta
        })  , HTTP_200_OK
 

@bookmarks.get("/<int:id>")
# @swag_from('./docs/bookmarks/.yaml')
@jwt_required()
def get_bookmark(id):
    current_user= get_jwt_identity()
    bookmark= Bookmark.query.filter_by(user_id= current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message": "Item not found"
        }), HTTP_404_NOT_FOUND
    
    else:
        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_200_OK


@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
# @swag_from('./docs/bookmarks/.yaml')
@jwt_required()
def update_bookmark(id):
    current_user= get_jwt_identity()
    bookmark= Bookmark.query.filter_by(user_id= current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message": "Item not found"
        }), HTTP_404_NOT_FOUND

    body= request.get_json().get('body', '')
    url= request.get_json().get('url', '')
    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST        
    
    bookmark.url= url
    bookmark.body= body

    db.session.commit()

    return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_200_OK


@bookmarks.delete("/<int:id>")
# @swag_from('./docs/bookmarks/.yaml')
@jwt_required()
def delete_bookmark(id):
    current_user= get_jwt_identity()
    bookmark= Bookmark.query.filter_by(user_id= current_user, id=id).first()

    if not bookmark:
        return jsonify({
            "message": "Item not found"
        }), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({
        "message": "Bookmark with id: {}, has being deleted successfully".format(id)
    }), HTTP_204_NO_CONTENT


@bookmarks.get("/stats")
@jwt_required()
@swag_from('./docs/bookmarks/stats.yaml')
def get_stats():
    current_user = get_jwt_identity()
    data= []

    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link={
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url
        }

        data.append(new_link)
    return jsonify({
        'data': data, 
    })    ,HTTP_200_OK
