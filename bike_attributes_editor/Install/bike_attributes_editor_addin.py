import arcpy
import pythonaddins
MXD = arcpy.mapping.MapDocument('CURRENT')
undo_stack = list()
redo_stack = list()

class BikeLanesComboBox(object):
    """Implementation for bike_attributes_editor_addin.BikeFacilityComboBox (ComboBox)"""
    def __init__(self):
        global bike_lanes_cv
        self.items = []
        self.bike_lanes_dict = {}
        arcpy.DomainToTable_management(r'Database Connections\OSM_Sockeye.sde', 'BikeLanes2', 'in_memory/bike_lanes_cv', 'codeField', 'descriptionField') 
        with arcpy.da.SearchCursor('in_memory/bike_lanes_cv', ['codeField', 'descriptionField']) as cursor:             
                for row in cursor: 
                    self.bike_lanes_dict[row[1]] = row[0]
                    self.items.append(row[1])
        #arcpy.Delete_management("in_memory/bike_lanes_cv")
        bike_lanes_cv = self.bike_lanes_dict['Yes']
        #self.cvd_dict = self.getCVDDict()
        #self.items = ["item1", "item2"]
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWW'
        self.width = 'WWW'
        self.value = "Yes"
    def onSelChange(self, selection):
        global bike_lanes_cv
        bike_lanes_cv = self.bike_lanes_dict[selection]
        pass
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
    #def getCVDDict(self):
    #    cvd_dict = {}
    #    arcpy.DomainToTable_management(r'Database Connections\OSM_Sockeye.sde', 'dBikeLanes', 'in_memory/cvdTable', 'codeField', 'descriptionField') 
    #    for row in arcpy.SearchCursor('in_memory/cvdTable'):
    #        cvd_dict[row[0]] = row[1]
    #    return cvd_dict

class BikeFacilityComboBox(object):
    """Implementation for bike_attributes_editor_addin.BikeFacilityComboBox (ComboBox)"""
    def __init__(self):
        global coded_value
        self.items = []
        self.cvd_dict = {}
        arcpy.DomainToTable_management(r'Database Connections\OSM_Sockeye.sde', 'dBikeLanes', 'in_memory/cvdTable', 'codeField', 'descriptionField') 
        with arcpy.da.SearchCursor('in_memory/cvdTable', ['codeField', 'descriptionField']) as cursor:             
                for row in cursor: 
                    self.cvd_dict[row[1]] = row[0]
                    self.items.append(row[1])
        arcpy.Delete_management("in_memory/cvdTable")
        coded_value = self.cvd_dict['NoBikeLane']
        #self.cvd_dict = self.getCVDDict()
        #self.items = ["item1", "item2"]
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWWWWWWWWWWWWWWWWWWWWWW'
        self.width = 'WWWWWWWWWWWWWW'
        self.value = "NoBikeLane"
    def onSelChange(self, selection):
        global coded_value
        coded_value = self.cvd_dict[selection]
        pass
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass
    #def getCVDDict(self):
    #    cvd_dict = {}
    #    arcpy.DomainToTable_management(r'Database Connections\OSM_Sockeye.sde', 'dBikeLanes', 'in_memory/cvdTable', 'codeField', 'descriptionField') 
    #    for row in arcpy.SearchCursor('in_memory/cvdTable'):
    #        cvd_dict[row[0]] = row[1]
    #    return cvd_dict

class DirectionComboBox(object):
    """Implementation for bike_attributes_editor_addin.DirectionComboBox (ComboBox)"""
    def __init__(self):
        global dir
        self.items = ["IJ", "JI", "Both"]
        self.editable = True
        self.enabled = True
        self.dropdownWidth = 'WWW'
        self.width = 'WWW'
        self.value = 'Both'
        dir = 'Both'
    def onSelChange(self, selection):
        global dir
        dir = selection
    def onEditChange(self, text):
        pass
    def onFocus(self, focused):
        pass
    def onEnter(self):
        pass
    def refresh(self):
        pass

class RedoButton(object):
    """Implementation for bike_attributes_editor_addin.RedoButton (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        global undo_stack
        global redo_stack

        if len(redo_stack) > 0:
            # Get the last item in the edit stack
            edit = redo_stack.pop()
            # Clear any existing selection on the layer, or else the cursor may
            #   not hit the necessary feature
            arcpy.SelectLayerByAttribute_management(edit[0], 'CLEAR_SELECTION')
            # A where clause to select the most recently edited feature
            wc = '{} = {}'.format(edit[2], edit[3])

            with arcpy.da.UpdateCursor(edit[0], edit[1], wc) as cur:
                for row in cur:
                    # Update the undo edit stack
                    edit_out = list(edit[:-1])
                    edit_out.append(row[0])
                    undo_stack.append(edit_out)
                    # Apply the edit
                    row[0] = edit[4]
                    cur.updateRow(row)
                    break

        arcpy.RefreshActiveView()


class UndoButton(object):
    """Implementation for bike_attributes_editor_addin.UndoButton (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        global undo_stack
        global redo_stack

        if len(undo_stack) > 0:
            edit = undo_stack.pop()

            arcpy.SelectLayerByAttribute_management(edit[0], 'CLEAR_SELECTION')
            wc = '{} = {}'.format(edit[2], edit[3])

            with arcpy.da.UpdateCursor(edit[0], edit[1], wc) as cur:
                for row in cur:
                    edit_out = list(edit[:-1])
                    edit_out.append(row[0])
                    redo_stack.append(edit_out)
                    row[0] = edit[4]
                    cur.updateRow(row)
                    break

        arcpy.RefreshActiveView()

class UpdateBikeAttributesButton(object):
    """Implementation for bike_attributes_editor_addin.UpdateBikeAttributesButton (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        lyr = 'OSMtest.DBO.modeAttributes'

        # Get a count of selected features in the selected layer
        fid_set = arcpy.Describe(lyr).FIDSet
        if fid_set == '':
            count = 0
        else:
            count = len(fid_set.split(';'))

        # If at least one feature is selected
        if count > 0:
            # Enable global modification of the undo_stack
            global undo_stack

            # Get the name of the layer's OID field
            fn_oid = arcpy.Describe(lyr).OIDFieldName

            with arcpy.da.UpdateCursor(lyr,[fn_oid, 'IJBikeLanes', 'JIBikeLanes', 'IJBikeFacility', 'JIBikeFacility']) as cursor:
                for row in cursor:
                    if dir == 'Both':
                        undo_stack.append((lyr, 'IJBikeLanes', fn_oid, row[0], row[1]))
                        undo_stack.append((lyr, 'JIBikeLanes', fn_oid, row[0], row[2]))
                        undo_stack.append((lyr, 'IJBikeFacility', fn_oid, row[0], row[3]))
                        undo_stack.append((lyr, 'JIBikeFacility', fn_oid, row[0], row[4]))
                        row[1] = bike_lanes_cv
                        row[2] = bike_lanes_cv
                        row[3] = coded_value
                        row[4] = coded_value
                    elif dir == 'IJ':
                        undo_stack.append((lyr, 'IJBikeLanes', fn_oid, row[0], row[1]))
                        undo_stack.append((lyr, 'IJBikeFacility', fn_oid, row[0], row[3]))
                        row[1] = bike_lanes_cv
                        row[3] = coded_value
                    else:
                        undo_stack.append((lyr, 'JIBikeLanes', fn_oid, row[0], row[2]))
                        undo_stack.append((lyr, 'JIBikeFacility', fn_oid, row[0], row[4]))
                        row[2] = bike_lanes_cv
                        row[4] = coded_value
                    cursor.updateRow(row)
            pythonaddins.MessageBox('Updated %s rows!' % (len(edge_list)), 'title')
        #pythonaddins.MessageBox('Have you applied a definition query to all necessary layers?', 'Query check', 4)  