from flask.ext.wtf import Form, HiddenField, IntegerField, Length, RadioField,\
  SelectField, SubmitField, TextField, TextAreaField, required

#from flaskext.babel import lazy_gettext as _
from flask.ext.babel import gettext as _


class GroupForm(Form):

  name = TextField(_("Name"),
                   validators=[required(message=_("Name is required."))])

  description = TextAreaField(_("Description"))
