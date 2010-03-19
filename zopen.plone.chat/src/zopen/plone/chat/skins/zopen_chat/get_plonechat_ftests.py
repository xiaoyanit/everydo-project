## Script (Python) "get_plonechat_ftests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selenium = context.portal_selenium
suite = selenium.getSuite()
target_language='en'
suite.setTargetLanguage(target_language)

selenium.addUser(id = 'sampleadmin',fullname='Sample Admin',roles=['Member', 'Manager',])
selenium.addUser(id = 'samplemember',fullname='Sample Member',roles=['Member',])

test_logout = suite.TestLogout()
test_admin_login  = suite.TestLoginPortlet('sampleadmin')
test_member_login  = suite.TestLoginPortlet('samplemember')
test_switch_language = suite.TestSwitchToLanguage()

plone21 = selenium.getPloneVersion() > "2.0.5"

if plone21:
    delete_from_folder = "/folder_delete?paths:list=" + suite.getTest().base + '/'
else:
    delete_from_folder = "/folder_delete?ids:list="

suite.addTests("PloneChat",
    'Login as Sample Admin',
    test_admin_login,
    test_switch_language,
    'Admin adds PloneChat',
    suite.open(delete_from_folder + 'plonechat'),
     suite.open("/"),
    suite.clickAndWait( "link=View"),
    suite.clickAndWait( "link=Chat"),
    suite.type("name=id","plonechat"),
    suite.clickAndWait("name=form_submit"),
    suite.verifyTextPresent("Please correct the indicated errors."),
    suite.type("name=title","Plonechat"),
    suite.clickAndWait("name=form_submit"),
    suite.verifyTextPresent("Your changes have been saved."),
    "Admin chats",
    suite.open("/plonechat"),
    suite.type("dummy_message","Dummy message"),
    suite.click("button_post_message"),
    suite.waitForValue("dummy_message", ""),
     )

return suite
