from datetime import datetime
from flow import GetField, FieldsTransform, ModelObjectCreate, Lambda, Action
from .model import User, Post, Tag


class RenameFields(Action):
    """ RenameFields renames data fields

    This is example of how user defined actions can be combined in workflows
    """
    def __init__(self, fields_map):
        """
        Parameters
        ----------
        fields_map : dict - key: old name, value: new name
        """
        super(RenameFields, self).__init__()
        self.fields_map = fields_map

    def do(self, data):
        for old, new in self.fields_map.items():
            if old in data:
                data[new] = data.pop(old)
        return data


_transform = FieldsTransform(
    {'published_parsed': lambda struct_time: datetime(*struct_time[:6]),
     'author': ModelObjectCreate(orm_model=User, fields=['name'], unique=['name']),
     'tags': Lambda(lambda ll: [el['term'] for el in ll]).for_each(ModelObjectCreate(orm_model=Tag,
                                                                                     fields=['name'],
                                                                                     unique=['name'])).root})

_store = ModelObjectCreate(orm_model=Post,
                           fields=['title', 'guid', 'link', 'date', 'user', 'tags'],
                           fields_map={'guid': 'id', 'date': 'published_parsed', 'user': 'author'},
                           unique=['guid'])

feed_extractor = GetField('entries')\
                    .for_each(RenameFields({'updated_parsed': 'published_parsed'}))\
                    .then(_transform)\
                    .then(_store).root
