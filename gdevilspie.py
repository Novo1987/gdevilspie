#!/usr/bin/python
#
# main.py
# Copyright (C) Islam Amer 2008 <iamer@open-craft.com>
# 
# main.py is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# main.py is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    import os
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gtk.glade
except:
    print "pyGTK is not correctly installed, exiting."
    quit()

match_criteria=["window_name", "window_role", "window_class", "window_xid", "application_name", "window_property", "window_workspace"]

class gdevilspie:
  def __init__(self):
    self.gladefile="gdevilspie.glade"
    try:
        self.wTreeList = gtk.glade.XML (self.gladefile, "RulesList")
    except:
        print "Glade file not found, exiting."
        quit()
    
    self.wTreeEdit = gtk.glade.XML (self.gladefile, "RuleEdit")

    self.RulesList = self.wTreeList.get_widget("RulesList")
    self.RuleEdit = self.wTreeEdit.get_widget("RuleEdit")
    self.RulesTree = self.wTreeList.get_widget("RulesTree")
    self.MatchTree = self.wTreeEdit.get_widget("MatchTree")
    self.MatchPropertyParameters_notebook = self.wTreeEdit.get_widget("MatchOptions_NoteBook1")
    
    self.wTreeList.signal_autoconnect (self)
    self.wTreeEdit.signal_autoconnect (self)

    self.rules_list_store = gtk.ListStore(str)
    self.match_list_store = gtk.ListStore(bool, str)
    
    self.RulesTree.set_model(self.rules_list_store)
    self.MatchTree.set_model(self.match_list_store)

    self.RulesFilesNames=gtk.TreeViewColumn('Rule Name')
    self.RulesTree.append_column(self.RulesFilesNames)
    self.RuleFileName=gtk.CellRendererText()
    self.RulesFilesNames.pack_start(self.RuleFileName,expand=True)
    self.RulesFilesNames.add_attribute(self.RuleFileName, 'text', 0)
    
    self.MatchPropertyNames=gtk.TreeViewColumn('Property')
    self.MatchPropertyEnable=gtk.TreeViewColumn('')
    self.MatchTree.append_column(self.MatchPropertyEnable)
    self.MatchTree.append_column(self.MatchPropertyNames)
    self.MatchPropertyName=gtk.CellRendererText()
    self.MatchPropertyEnable=gtk.CellRendererToggle()
    self.MatchPropertyEnable.set_property("activatable", 1)
    
    self.MatchPropertyNames.pack_start(self.MatchPropertyEnable,expand=False)
    self.MatchPropertyNames.pack_start(self.MatchPropertyName,expand=True)

    self.MatchPropertyNames.add_attribute(self.MatchPropertyEnable, 'active', False)
    self.MatchPropertyNames.add_attribute(self.MatchPropertyName, 'text', 1)
    for MatchProperty in match_criteria:
        self.match_list_store.append([0, MatchProperty])
    
    self.MatchPropertyEnable.connect("toggled", self.MatchPropertyEnable_toggle)
    
    self.RulesList.show_all()  
  
  def MatchPropertyEnable_toggle(self, widget, path):
    self.MatchPropertyParameters_notebook.set_current_page(int(path))
    iter = self.match_list_store.get_iter_from_string(path)
    CurrentState = self.match_list_store.get_value(iter, 0)
    self.match_list_store.set_value(iter, 0 , not CurrentState )
    
  def on_RulesList_destroy(self,widget):
    gtk.main_quit()

  def on_Quit_clicked(self, widget):
    gtk.main_quit()

  def on_AddRule_clicked(self,widget):
    self.RuleEdit.show()

  def on_RuleEdit_destroy(self,widget):
    self.RuleEdit.hide()

  def on_Cancel_clicked(self,widget):
    self.RuleEdit.hide()

  def on_Save_clicked(self,widget):
   self.RuleEdit.hide()

  def on_DeleteRule_clicked(self,widget):
   SelectedRow = self.RulesTree.get_selection()
   (model, iter) = SelectedRow.get_selected()
   if (iter != None):
     SelectedRule = self.rules_list_store.get(iter, 0)
     RuleFile = os.path.expanduser("~/.devilspie/") + SelectedRule[0] + '.ds'
     os.remove(RuleFile)
     self.rules_list_store.remove(iter)

  def main(self):
    dir = os.path.expanduser("~/.devilspie")
    if (os.path.exists(dir)):
      if (os.path.isdir(dir)):
        rulefileslist = os.listdir(dir)
        for rulefile in rulefileslist:
            if (rulefile.endswith(".ds")):
                rulefile=rulefile.replace(".ds","")
                self.rules_list_store.append([rulefile])
      else:
          print "~/.devilspie is a file, please remove it"
    else:
          os.makedirs(dir)
    
    
    gtk.main()

if __name__ == "__main__":
    prog=gdevilspie()
    prog.main()