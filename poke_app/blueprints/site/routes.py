from flask import Blueprint, render_template 



#need to instantiate our Blueprint class
site = Blueprint('site', __name__, template_folder='site_templates' )


#use site object to create our routes
@site.route('/')
def pokecenter():
    return render_template('pokecenter.html')