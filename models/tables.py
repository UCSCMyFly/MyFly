# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

db.define_table('user_nodes',
				Field('user_email' ,default=auth.user.email if auth.user_id else None),
				Field('sources', 'list:string', default=[]),
				Field('destinations', 'list:string', default=[]),
				Field('dest_prices', 'list:integer', default=[]),
				)

db.define_table('airports',
				Field('airport_name', 'string'),
				)



# db.source_ap.name.widgit = SQLFORM.widgets.autocomplete(
#      request, db.airports.airport_name, limitby=(0,10), min_length=2)

# db.destination_ap.name.widgit = SQLFORM.widgets.autocomplete(
#      request, db.airports.airport_name, limitby=(0,10), min_length=2)


# I don't want to display the user email by default in all forms.

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
