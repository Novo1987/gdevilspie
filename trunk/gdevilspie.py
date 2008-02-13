#!/usr/bin/python
#
# gdevilspie.py
# Copyright (C) Islam Amer 2008 <iamer@open-craft.com>
# 
# gdevilspie.py is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# gdevilspie.py is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import needed models

try:
    import os
    import sys
    import gobject
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gtk.glade
except:
    print "pyGTK is not correctly installed, exiting."
    sys.exit(1)


# List of possible match criteria
match_criteria={
"window_name" : { 
"description" : "<b>Any window whose name</b>", "widget" : None, 
"entry_is" : None, "entry_contains" : None, "entry_matches" : None,
"is_not" : False, "contains_not" : False, "matches_not" : False }, 

"window_role" : { "description" : "<b>Any window whose role</b>", "widget" : None, 
"entry_is" : None, "entry_contains" : None, "entry_matches" : None ,
"is_not" : False, "contains_not" : False, "matches_not" : False }, 

"window_class" : { "description" : "<b>Any window whose class</b>", "widget" : None, 
"entry_is" : None, "entry_contains" : None, "entry_matches" : None ,
"is_not" : False, "contains_not" : False, "matches_not" : False }, 

"window_xid" : { "description" : "<b>Any window whose xid</b>", "widget" : None, 
"entry_is" : None, "entry_contains" : None, "entry_matches" : None ,
"is_not" : False, "contains_not" : False, "matches_not" : False }, 

"application_name" : { "description" : "<b>Any window whose application name</b>", "widget" : None,
"entry_is" : None, "entry_contains" : None, "entry_matches" : None ,
"is_not" : False, "contains_not" : False, "matches_not" : False }, 

"window_property" : { "description" : "<b>Any window whose property</b>", "widget" : None, 
"entry_is" : None, "entry_contains" : None, "entry_matches" : None ,
"is_not" : False, "contains_not" : False, "matches_not" : False }, 

"window_workspace" : { "description" : "<b>Any window whose workspace</b>", "widget" : None, 
"entry_is" : None, "entry_contains" : None, "entry_matches" : None ,
"is_not" : False, "contains_not" : False, "matches_not" : False } 
}

def toggle_this(widget, str, match_criteria_name):
    match_criteria[match_criteria_name][str+"_not"]= not match_criteria[match_criteria_name][str+"_not"]
    return

def create_match_parameters_page(match_criteria_name):
    vbox = gtk.VBox()
    str = match_criteria[match_criteria_name]["description"]
    description_text = gtk.Label(str)
    description_text.set_use_markup(True)
    description_text.set_line_wrap(True)
    vbox.pack_start(description_text, False, False)
    
    # three hboxes
    hbox_is, hbox_contains, hbox_matches = gtk.HBox(), gtk.HBox(), gtk.HBox()

    # Three Check boxes for negation
    negate_checkbox_is, negate_checkbox_contains, negate_checkbox_matches = gtk.CheckButton("does not"), gtk.CheckButton("does not"), gtk.CheckButton("does not")
    # We have to reflect the check box state somewhere
    negate_checkbox_is.connect("toggled", toggle_this, "is", match_criteria_name)
    negate_checkbox_contains.connect("toggled", toggle_this, "contains", match_criteria_name)
    negate_checkbox_matches.connect("toggled", toggle_this, "matches", match_criteria_name)
       
    # Three text entries
    match_criteria[match_criteria_name]["entry_is"] = gtk.Entry()
    match_criteria[match_criteria_name]["entry_contains"] = gtk.Entry()
    match_criteria[match_criteria_name]["entry_matches"] = gtk.Entry()

    entry_is = match_criteria[match_criteria_name]["entry_is"]
    entry_contains = match_criteria[match_criteria_name]["entry_contains"]
    entry_matches = match_criteria[match_criteria_name]["entry_matches"]

    # Three labels
    MatchMethod_text_is=gtk.Label("equals")
    MatchMethod_text_contains=gtk.Label("contains")
    MatchMethod_text_matches=gtk.Label("matches")
    
    # Pack the triads
    hbox_is.pack_start(negate_checkbox_is, False, False)
    hbox_contains.pack_start(negate_checkbox_contains, False, False)
    hbox_matches.pack_start(negate_checkbox_matches, False, False)
    
    hbox_is.pack_end(entry_is, False, False)
    hbox_contains.pack_end(entry_contains, False, False)
    hbox_matches.pack_end(entry_matches, False, False)
    
    hbox_is.pack_end(MatchMethod_text_is, True, False)
    hbox_contains.pack_end(MatchMethod_text_contains, True, False)
    hbox_matches.pack_end(MatchMethod_text_matches, True, False)
    
    # pack the rows
    vbox.pack_start(hbox_is, True, False)
    vbox.pack_start(hbox_contains, True, False)
    vbox.pack_start(hbox_matches, True, False)
    
    # return the vbox we built so it gets packed into the property page 
    return vbox
    


# Dictionary of the actions for each of which we store a dictionary of help text and widgets
actions_dict={"geometry" : None,
"fullscreen" : None,
"focus": None,
"center": None,
"maximize": None,
"maximize_vertically": None,
"maximize_horizontally": None,
"unmaximize": None,
"minimize": None,
"unminimize": None,
"shade": None,
"unshade": None,
"close": None,
"pin": None,
"unpin": None,
"stick": None,
"unstick": None,
"set_workspace": None,
"set_viewport": None,
"skip_pager": None,
"skip_tasklist": None,
"above": None,
"below": None,
"decorate": None,
"undecorate": None,
"wintype": None,
"opacity": None,
"spawn_async": None,
"spawn_sync": None }

# Glade file used in all classes
gladefile="gdevilspie.glade"

# Directory where we store .ds files
dir = os.path.expanduser("~/.devilspie")

# The main class which creates the main window where we list the rules
class RulesListWindow:
# Initialization of the class
  def __init__(self):
    try:
    # try to get our widgets from the gladefile
	wTreeList = gtk.glade.XML (gladefile, "RulesList")
    except:
    #inform the user there was an error and exit
        gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Glade file not found, exiting.").run()
        quit()

    # Get the widgets that we will work with RulesList is the window, and RulesTree is the tree list of rules
    self.RulesList = wTreeList.get_widget("RulesList")
    self.RulesTree = wTreeList.get_widget("RulesTree")
    
    # connect the signals to callbacks
    wTreeList.signal_autoconnect (self)

    # create a liststore model which takes one string, the rule name
    self.rules_list_store = gtk.ListStore(str)

    # connect the model to the tree view
    self.RulesTree.set_model(self.rules_list_store)

    # pack a single column that has a text cell into the tree view
    self.RulesFilesNames=gtk.TreeViewColumn('Rule Name')
    self.RulesTree.append_column(self.RulesFilesNames)
    self.RuleFileName=gtk.CellRendererText()
    self.RulesFilesNames.pack_start(self.RuleFileName,expand=True)
    self.RulesFilesNames.add_attribute(self.RuleFileName, 'text', 0)
    
    # if we have a config dir list the files inside otherwise try to create it
    if (os.path.exists(dir)):
      if (os.path.isdir(dir)):
        self.fill_rules_list()
      else:
          print "~/.devilspie is a file, please remove it"
    else:
          os.makedirs(dir)

    # display the main window
    self.RulesList.show_all()  

  # handle exiting the program  
  def on_RulesList_destroy(self,widget):
    gtk.main_quit()

  def on_Quit_clicked(self, widget):
    gtk.main_quit()

  # make a rule creator instance
  def on_AddRule_clicked(self,widget):
    RuleEdit = RuleEditorWindow()
  
  # used to delete a rule
  def on_DeleteRule_clicked(self,widget):
   SelectedRow = self.RulesTree.get_selection()
   (model, iter) = SelectedRow.get_selected()
   if (iter != None):
     SelectedRule = self.rules_list_store.get(iter, 0)
     RuleFile = os.path.expanduser("~/.devilspie/") + SelectedRule[0] + '.ds'
     if (os.path.exists(RuleFile)):
       try:
         os.remove(RuleFile)
         self.rules_list_store.remove(iter)
       except:
         error_dialog = gtk.MessageDialog(self.RuleEdit, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CANCEL, "Could not save the rule, please check file permissions and try again.")
         response = error_dialog.run()
         error_dialog.destroy()
  
  # used to update the list after a delete or add  
  def update_rules_list(self):
    self.rules_list_store.clear()
    self.fill_rules_list()
  
  # fill up the rules list with the names of the files that end with .ds  
  def fill_rules_list(self):
    rulefileslist = os.listdir(dir)
    for rulefile in rulefileslist:
      if (rulefile.endswith(".ds")):
        rulefile=gobject.filename_display_name(rulefile)
        rulefile=rulefile.replace(".ds","")
        self.rules_list_store.append([rulefile])

# This is the rule creator window
class RuleEditorWindow:
  def __init__(self):
  # try to get our widgets from the gladefile
    try:
	wTreeEdit = gtk.glade.XML (gladefile, "RuleEdit")
    except:
        gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Glade file not found, exiting.").run()
        quit()

    # get the widgets that we use
    # the window
    self.RuleEdit = wTreeEdit.get_widget("RuleEdit")
    # Match tree
    self.MatchTree = wTreeEdit.get_widget("MatchTree")
    # Actions tree
    self.ActionsTree = wTreeEdit.get_widget("ActionsTreeList")
    # Match parameters notebook
    self.MatchPropertyParameters_notebook = wTreeEdit.get_widget("MatchPropertyParameters_notebook")
    # Action parameters notebook
    self.ActionsParameters_notebook = wTreeEdit.get_widget("ActionsParameters_notebook")
    # rule name text box
    self.RuleName_entry = wTreeEdit.get_widget("RuleName_entry")

    # Connect to our signals
    wTreeEdit.signal_autoconnect (self)

    # create list stores and connect the models to the tree views
    self.match_list_store = gtk.ListStore(bool, str)
    self.actions_list_store = gtk.ListStore(bool,str)
    self.MatchTree.set_model(self.match_list_store)
    self.ActionsTree.set_model(self.actions_list_store)

    # Action tree has two columns with two cells. One cell is a checkbox and the other is text
    self.ActionsNames_column=gtk.TreeViewColumn('Action')
    self.ActionsEnable_column=gtk.TreeViewColumn('')
    self.ActionsTree.append_column(self.ActionsEnable_column)
    self.ActionsTree.append_column(self.ActionsNames_column)
    self.ActionsNames_cell=gtk.CellRendererText()
    self.ActionsEnable_cell=gtk.CellRendererToggle()
    self.ActionsEnable_cell.set_property("activatable", 1)
    
    self.ActionsEnable_column.pack_start(self.ActionsEnable_cell, expand=True)
    self.ActionsNames_column.pack_start(self.ActionsNames_cell, expand=True)
    
    self.ActionsNames_column.add_attribute(self.ActionsNames_cell, 'text', 1)
    self.ActionsEnable_column.add_attribute(self.ActionsEnable_cell, 'active', False)
    
    # Fill up the actions list store from the dictionary and create notebook pages for their parameters
    for Action in actions_dict:
      self.actions_list_store.append([0, Action])
      actions_dict[Action] = gtk.Label(Action)
      self.ActionsParameters_notebook.insert_page(actions_dict[Action], None)
    
    # Reflect the checkbox state in the model
    self.ActionsEnable_cell.connect("toggled", self.ActionsEnable_toggle)
    # Flip the notebook pages when the selection changes
    self.ActionsTree.connect("cursor-changed", self.Actions_selected)
    
    # Match tree has two columns with two cells. One cell is a checkbox and the other is text
    self.MatchPropertyNames_column=gtk.TreeViewColumn('Property')
    self.MatchPropertyEnable_column=gtk.TreeViewColumn('')
    self.MatchTree.append_column(self.MatchPropertyEnable_column)
    self.MatchTree.append_column(self.MatchPropertyNames_column)
    self.MatchPropertyName_cell=gtk.CellRendererText()
    self.MatchPropertyEnable_cell=gtk.CellRendererToggle()
    self.MatchPropertyEnable_cell.set_property("activatable", 1)
    
    self.MatchPropertyEnable_column.pack_start(self.MatchPropertyEnable_cell, expand=True)
    self.MatchPropertyNames_column.pack_start(self.MatchPropertyName_cell, expand=True)

    self.MatchPropertyEnable_column.add_attribute(self.MatchPropertyEnable_cell, 'active', False)
    self.MatchPropertyNames_column.add_attribute(self.MatchPropertyName_cell, 'text', 1)

    # Fill up the actions list store from the dictionary and create notebook pages for their parameters
    for MatchProperty in match_criteria:
        self.match_list_store.append([0, MatchProperty])
        #match_criteria[MatchProperty] = gtk.Label(MatchProperty)
        match_criteria[MatchProperty]["widget"] = create_match_parameters_page(MatchProperty)
        self.MatchPropertyParameters_notebook.insert_page(match_criteria[MatchProperty]["widget"], None)
    
    self.MatchPropertyEnable_cell.connect("toggled", self.MatchPropertyEnable_toggle)
    self.MatchTree.connect("cursor-changed", self.MatchPropertyRow_selected)
    
    self.RuleEdit.show_all()
    
  def Actions_selected(self, widget):
    selected_row = self.ActionsTree.get_selection()
    (model, iter) = selected_row.get_selected()
    if (iter != None):
      path = model.get_string_from_iter(iter)
      self.ActionsParameters_notebook.set_current_page(int(path))
      self.ActionsParameters_notebook.show()
    
  def ActionsEnable_toggle(self, widget, path):
    iter = self.actions_list_store.get_iter_from_string(path)
    CurrentState = self.actions_list_store.get_value(iter, 0)
    self.actions_list_store.set_value(iter, 0 , not CurrentState)
  
  def MatchPropertyRow_selected(self, widget):
    selected_row = self.MatchTree.get_selection()
    (model, iter) = selected_row.get_selected()
    if (iter != None):
      path = model.get_string_from_iter(iter)
      self.MatchPropertyParameters_notebook.set_current_page(int(path))
  
  def MatchPropertyEnable_toggle(self, widget, path):
    iter = self.match_list_store.get_iter_from_string(path)
    CurrentState = self.match_list_store.get_value(iter, 0)
    self.match_list_store.set_value(iter, 0 , not CurrentState )
  
  def on_RuleEdit_destroy(self,widget):
    self.RuleEdit.destroy()
    
  def on_Cancel_clicked(self,widget):
    self.RuleEdit.destroy()
    
  def on_Save_clicked(self,widget):
   str = self.RuleName_entry.get_text()
   self.Save_Rule(str)
   
  def Save_Rule(self, str):
    #do stuff to generate the rule.
    path = os.path.expanduser("~/.devilspie/")
    new_Rule_file_name = str + ".ds"
    rulefileslist = os.listdir(dir)
    if ( new_Rule_file_name in rulefileslist ):
      error_dialog = gtk.MessageDialog(self.RuleEdit, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, "The rule name you entered is already in use, do you want to overwrite it?")
      response = error_dialog.run()
      error_dialog.destroy()
      if ( response == gtk.RESPONSE_YES ):
        try:
          new_Rule_file_name = path + new_Rule_file_name
          f = open( new_Rule_file_name, 'w' )
          f.write( "# " + str )
          f.close()
          MainWindow.update_rules_list()
          self.RuleEdit.destroy()
        except:
          error_dialog = gtk.MessageDialog(self.RuleEdit, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CANCEL, "Could not save the rule, please check file permissions and try again.")
          response = error_dialog.run()
          error_dialog.destroy()
      else:
        pass


MainWindow = RulesListWindow()
gtk.main()
