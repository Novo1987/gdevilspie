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
    import commands
    import signal
    import subprocess
    import string
    import gobject
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gtk.glade
except:
    print "pyGTK is not correctly installed, exiting."
    sys.exit(1)

DISABLE_FILLER=""
try:
    import filler
except:
    error = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Make sure that Python-Wnck is correctly installed for 'filler' module to run properly.")
    response = error.run()
    error.destroy()
    DISABLE_FILLER="True"

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
    MatchMethod_text_is=gtk.Label("equal(s)")
    MatchMethod_text_contains=gtk.Label("contain(s)")
    MatchMethod_text_matches=gtk.Label("match(es)")
    
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
    

window_types=["normal", "dialog", "menu", "toolbar", "splash-screen", "utility", "dock", "desktop"]

# Dictionary of the actions for each of which we store a dictionary of help text and widgets
actions_dict={
		"geometry" : {"description" : "<b>Set position and size of window</b>", "widget" : None, "input" : { "xposition" : None, "yposition" : None, "width" : None, "height" : None } },
"fullscreen" : {"description" : "<b>Make the window fullscreen</b>", "widget" : None},
"focus": {"description" : "<b>Focus the window</b>", "widget" : None},
"center": {"description" : "<b>Center the position of the window</b>", "widget" : None},
"maximize": {"description" : "<b>Maximize the window</b>", "widget" : None},
"maximize_vertically": {"description" : "<b>Maximize the window vertically only</b>", "widget" : None},
"maximize_horizontally": {"description" : "<b>Maximize the window horizontally only</b>", "widget" : None},
"unmaximize": {"description" : "<b>Unmaximize the window</b>", "widget" : None},
"minimize": {"description" : "<b>Minimize the window</b>", "widget" : None},
"unminimize": {"description" : "<b>Unminimize the window</b>", "widget" : None},
"shade": {"description" : "<b>Roll up the window</b>", "widget" : None},
"unshade": {"description" : "<b>Roll down the window</b>", "widget" : None},
"close": {"description" : "<b>Close the window</b>", "widget" : None},
"pin": {"description" : "<b>Pin the window to all workspaces</b>", "widget" : None},
"unpin": {"description" : "<b>Unpin the window from all workspaces</b>", "widget" : None},
"stick": {"description" : "<b>Stick the window to all viewports</b>", "widget" : None},
"unstick": {"description" : "<b>Unstick the window from all viewports</b>", "widget" : None},
"set_workspace": {"description" : "<b>Move the window to a specific workspace number</b>", "widget" : None, "input" : { "workspace" : None } },
"set_viewport": {"description" : "<b>Move the window to a specific viewport number</b>", "widget" : None, "input" : { "viewport" : None } },
"skip_pager": {"description" : "<b>Remove the window from the window list</b>", "widget" : None},
"skip_tasklist": {"description" : "<b>Remove the window from the pager</b>", "widget" : None},
"above": {"description" : "<b>Set  the  current window to be above all normal windows</b>", "widget" : None},
"below": {"description" : "<b>Set the current window to be below all normal  windows</b>", "widget" : None},
"decorate": {"description" : "<b>Add  the  window  manager  decorations  to  the window</b>", "widget" : None},
"undecorate": {"description" : "<b>Remove the window manager decorations from  the window</b>", "widget" : None},
"wintype": {"description" : "<b>Set  the  window  type  of the window</b>", "widget" : None, "input" : { "type" : None } },
"opacity": {"description" : "<b>Change  the  opacity level of the widnow</b>", "widget" : None, "input" : { "opacity" : None } },
"spawn_async": {"description" : "<b>Execute a command in the background</b>", "widget" : None, "input" : { "command" : None } },
"spawn_sync": {"description" : "<b>Execute a command in the foreground</b>", "widget" : None, "input" : { "command" : None } }
}

def create_action_parameters_page(action_name):
    vbox = gtk.VBox()
    str = actions_dict[action_name]["description"]
    description_text = gtk.Label(str)
    description_text.set_use_markup(True)
    description_text.set_line_wrap(True)
    vbox.pack_start(description_text, True, False)
    if ( actions_dict[action_name].has_key("input") ):
      for key in actions_dict[action_name]["input"]:
	  hbox = gtk.HBox()
          label = gtk.Label(key)
	  entry = gtk.Entry()
	  actions_dict[action_name]["input"][key] = entry
	  hbox.pack_start(label, False, False)
	  hbox.pack_end(entry, False, False)
	  vbox.pack_start(hbox, True, True)
    return vbox


# generated rule storage

def generate_rule(generated_rule):
    part0 = "( if \n"
    part1 = "( and \n"
    part2 = generate_match_criteria()
    part3 = ") \n" + "( begin \n"
    part4 = generate_actions()
    part5 = "( println \"match\" )\n"
    part6 = ")\n)\n"
    generated_rule = part0 + part1 + part2 + part3 + part4 + part5 + part6
    return generated_rule

def generate_match_criteria():
  strous=""
  for row in MainWindow.RuleEdit.match_list_store:
    match_method = row[1]
    if ( row[0] == True ):
      for prop in ["is", "contains", "matches"]:
        entry = "entry_" + prop
        negation = prop + "_not"
        entry_text = match_criteria[match_method][entry].get_text()
        negation_state = match_criteria[match_method][negation]
        if ( entry_text != "" ):
          storing=""
          if ( negation_state == True ):
            storing = "( " + "not "+ "( " + prop
          else:
            storing = "( " + prop
          storing = storing + " ( " + match_method + " ) "
          storing = storing + '"' + entry_text + '"' + " )"
          if ( negation_state == True ):
            storing = storing + " )"
          storing = storing + "\n"
      strous += storing
  return strous

def generate_actions():
    strous = ""
    for row in MainWindow.RuleEdit.actions_list_store:
        action_name = row[1]
        if ( row[0] == True ):
            storing = action_name
            if actions_dict[action_name].has_key("input"):
                if ( action_name == "geometry" ):
                  geomstring = actions_dict[action_name]["input"]["width"].get_text()
                  geomstring = geomstring + "x" + actions_dict[action_name]["input"]["height"].get_text()
                  geomstring = geomstring + "+" + actions_dict[action_name]["input"]["xposition"].get_text()
                  geomstring = geomstring + "+" + actions_dict[action_name]["input"]["yposition"].get_text()
                  storing = storing + "\"" + geomstring + "\""
                else:
                  for key in actions_dict[action_name]["input"]:
                    storing = storing + " \"" + actions_dict[action_name]["input"][key].get_text() + "\""
            strous += "( " + storing + " )\n"
    return strous

# Glade file used in all classes
gladefile="gdevilspie.glade"

# Directory where we store .ds files
dir = os.path.expanduser("~/.devilspie")


# Tray Icon (Not working properly yet)
tray = gtk.StatusIcon()
tray.set_from_file("window-new.png")
tray.set_tooltip("gDevilspie")
tray.set_blinking(False)




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
    self.DaemonStatus = wTreeList.get_widget("DaemonStatus")
    self.ToggleDaemon = wTreeList.get_widget("ToggleDaemon")
    self.ToggleDaemonLabel = wTreeList.get_widget("ToggleDaemonLabel")
    
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
    
    self.UpdateDaemonStatus()

    # display the main window
    self.RulesList.show_all()  

  # handle exiting the program  
  def on_RulesList_destroy(self,widget):
    gtk.main_quit()

  def on_Quit_clicked(self, widget):
    gtk.main_quit()

  # make a rule creator instance
  def on_AddRule_clicked(self,widget):
    self.RuleEdit = RuleEditorWindow()
  
  def UpdateDaemonStatus(self):
    prog = commands.getoutput("pgrep -x devilspie")
    if ( prog == "" ):
      # daemon not running
      self.DaemonStatus.set_markup("<b>The devilspie daemon is <span foreground=\"red\">not</span> running  </b>")
      self.ToggleDaemonLabel.set_markup("<span foreground=\"green\">Start it ?</span>")
      return 1
    else:
      self.DaemonStatus.set_markup("<b>The devilspie daemon is <span foreground=\"green\">running</span>  </b>")
      self.ToggleDaemonLabel.set_markup("<span foreground=\"red\">Stop it ?</span>")
      return prog
    
  def toggle_daemon(self):
    status = self.UpdateDaemonStatus()
    if ( status == 1 ):
      if (os.fork() == 0):
        if (os.fork() == 0):
          os.execvpe('devilspie', ['-a'] , os.environ)
          sys.exit(0)
        else:
          sys.exit(0)
      else:
        os.wait()
    else:
      # kill it
      os.kill(int(status),signal.SIGKILL)
    status = self.UpdateDaemonStatus()
    
  def on_ToggleDaemon_clicked(self,widget):
    self.toggle_daemon()
  
  # used to delete a rule
  def on_DeleteRule_clicked(self,widget):
   SelectedRow = self.RulesTree.get_selection()
   (model, iter) = SelectedRow.get_selected()
   if (iter != None):
     SelectedRule = self.rules_list_store.get(iter, 0)
     RuleFile = os.path.expanduser("~/.devilspie/") + SelectedRule[0] + '.ds'
     if (os.path.exists(RuleFile)):
       try:
         error_dialog = gtk.MessageDialog(self.RulesList, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, "Are you sure you want to remove the rule " + SelectedRule[0] + "?")
         response = error_dialog.run()
         error_dialog.destroy()
         if ( response == gtk.RESPONSE_YES ):
           os.remove(RuleFile)
           self.rules_list_store.remove(iter)
         else:
           return
       except:
         error_dialog = gtk.MessageDialog(self.RulesList, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CANCEL, "Could not remove the rule, please check file permissions and try again.")
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
      #actions_dict[Action] = gtk.Label(Action)
      actions_dict[Action]["widget"] = create_action_parameters_page(Action)
      self.ActionsParameters_notebook.insert_page(actions_dict[Action]["widget"], None)
    
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
    
  def on_Fill_clicked(self,widget):
    if (DISABLE_FILLER == "True"):
      error = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "The filler is disabled.")
      response = error.run()
      error.destroy()
    else:
      self.filler_window = FillerWindow()

  def on_Cancel_clicked(self,widget):
    self.RuleEdit.destroy()
    
  def on_Save_clicked(self,widget):
   str = self.RuleName_entry.get_text()
   self.Save_Rule(str)
   
  def Save_Rule(self, str):
    if ( str == "" ):
      return
    path = os.path.expanduser("~/.devilspie/")
    new_Rule_file_name = str + ".ds"
    rulefileslist = os.listdir(dir)
    response = gtk.RESPONSE_YES
    if ( new_Rule_file_name in rulefileslist ):
      error_dialog = gtk.MessageDialog(self.RuleEdit, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, "The rule name you entered is already in use, do you want to overwrite it?")
      response = error_dialog.run()
      error_dialog.destroy()
    if ( response == gtk.RESPONSE_YES ):
      try:
        new_Rule_file_name = path + new_Rule_file_name
        f = open( new_Rule_file_name, 'w' )
        f.write( "; generated_rule " + str + "\n")
        generated_rule = ""
        generated_rule = generate_rule(generated_rule)
        f.write( generated_rule )
        f.close()
        MainWindow.update_rules_list()
        self.RuleEdit.destroy()
      except:
        error_dialog = gtk.MessageDialog(self.RuleEdit, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CANCEL, "Could not save the rule, please check file permissions and try again.")
        response = error_dialog.run()
        error_dialog.destroy()
    else:
        pass

class FillerWindow:
  def __init__(self):
    try:
    # try to get our widgets from the gladefile
	wFillerList = gtk.glade.XML (gladefile, "FillerDialog")
    except:
    #inform the user there was an error and exit
        gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Glade file not found, exiting.").run()
        quit()

    self.FillerDialog = wFillerList.get_widget("FillerDialog")
    self.cancel_button = wFillerList.get_widget("Filler_Cancel")
    self.fill_button = wFillerList.get_widget("Filler_Apply")
    self.window_tree = wFillerList.get_widget("FillerTree")
    
    self.cancel_button.connect("clicked", self.on_Filler_Cancel_clicked)
    self.fill_button.connect("clicked", self.on_Filler_Apply_clicked)
    self.FillerDialog.connect("destroy", self.on_FillerDialog_destroy)
    self.window_liststore = gtk.ListStore(gobject.TYPE_STRING)
    self.window_name_cell = gtk.CellRendererText()
    self.window_names_column = gtk.TreeViewColumn("Available Windows")
    self.window_names_column.pack_start(self.window_name_cell, expand=True)
    self.window_names_column.add_attribute(self.window_name_cell, 'text', 0)
    
    self.window_tree.append_column(self.window_names_column)
    self.window_tree.set_model(self.window_liststore)
    self.windowlist, self.namelist = filler.Get_Windowname_List()
    for name in self.namelist:
      self.window_liststore.append([name])
    
    self.FillerDialog.show_all()

  def on_Filler_Apply_clicked(self, widget):
   selected_window = self.window_tree.get_selection()
   ( model , iter ) = selected_window.get_selected()
   path = model.get_path(iter)
   window_object = self.windowlist[path[0]]
   window_match_dict = filler.Matchdict_Window(window_object)
   window_action_dict = filler.Actiondict_Window(window_object)
   
   for key in window_match_dict:
     Entry = match_criteria[key]["entry_is"] 
     Entry.set_text(str(window_match_dict[key]))
   
   Entry = actions_dict["geometry"]["input"]["xposition"] 
   Entry.set_text(str(window_action_dict["xposition"]))
   Entry = actions_dict["geometry"]["input"]["yposition"] 
   Entry.set_text(str(window_action_dict["yposition"]))
   Entry = actions_dict["geometry"]["input"]["width"] 
   Entry.set_text(str(window_action_dict["width"]))
   Entry = actions_dict["geometry"]["input"]["height"] 
   Entry.set_text(str(window_action_dict["height"]))     
   Entry = actions_dict["set_workspace"]["input"]["workspace"] 
   Entry.set_text(str(window_action_dict["set_workspace"]))
   
   for row in MainWindow.RuleEdit.actions_list_store:
     if ( row[1] == "fullscreen"):
       if (window_action_dict["fullscreen"] == True):
         row[0] = True
     elif ( row[1] == "maximize"):
       if (window_action_dict["maximize"] == True):
         row[0] = True
     elif ( row[1] == "maximize_horizontally"):
       if (window_action_dict["maximize_horizontally"] == True):
         row[0] = True
     elif ( row[1] == "maximize_vertically"):
       if (window_action_dict["maximize_vertically"] == True):
         row[0] = True
     elif ( row[1] == "minimize"):
       if (window_action_dict["minimize"] == True):
         row[0] = True
     elif ( row[1] == "shade"):
       if (window_action_dict["shade"] == True):
         row[0] = True
     elif ( row[1] == "pin"):
       if (window_action_dict["pin"] == True):
         row[0] = True
     elif ( row[1] == "stick"):
       if (window_action_dict["stick"] == True):
         row[0] = True
     else:
       pass
   
   self.FillerDialog.destroy()

  def on_FillerDialog_destroy(self, widget):
   self.FillerDialog.destroy()
           
  def on_Filler_Cancel_clicked(self, widget):
   self.FillerDialog.destroy()



MainWindow = RulesListWindow()
gtk.main()
