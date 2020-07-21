import win32com.client
def WMIDateStringToDate(dtmDate):
    strDateTime = ""
    if (dtmDate[4] == 0):
        strDateTime = dtmDate[5] + '/'
    else:
        strDateTime = dtmDate[4] + dtmDate[5] + '/'
    if (dtmDate[6] == 0):
        strDateTime = strDateTime + dtmDate[7] + '/'
    else:
        strDateTime = strDateTime + dtmDate[6] + dtmDate[7] + '/'
        strDateTime = strDateTime + dtmDate[0] + dtmDate[1] + dtmDate[2] + dtmDate[3] + " " + dtmDate[8] + dtmDate[9] + ":" + dtmDate[10] + dtmDate[11] +':' + dtmDate[12] + dtmDate[13]
    return strDateTime

strComputer = "."
objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_Service")
for objItem in colItems:
    if objItem.AcceptPause != None:
        print("AcceptPause: %s" % objItem.AcceptPause)
    if objItem.AcceptStop != None:
        print("AcceptStop: %s" % objItem.AcceptStop)
    if objItem.Caption != None:
        print("Caption: %s" % objItem.Caption)
    if objItem.CheckPoint != None:
        print("CheckPoint: %s" % objItem.CheckPoint)
    if objItem.CreationClassName != None:
        print("CreationClassName: %s" % objItem.CreationClassName)
    if objItem.Description != None:
        print("Description: %s" % objItem.Description)
    if objItem.DesktopInteract != None:
        print("DesktopInteract: %s" % objItem.DesktopInteract)
    if objItem.DisplayName != None:
        print("DisplayName: %s" % objItem.DisplayName)
    if objItem.ErrorControl != None:
        print("ErrorControl: %s" % objItem.ErrorControl)
    if objItem.ExitCode != None:
        print("ExitCode: %s" % objItem.ExitCode)
    if objItem.InstallDate != None:
        print("InstallDate: %s" % WMIDateStringToDate(objItem.InstallDate))
    if objItem.Name != None:
        print("Name: %s" % objItem.Name)
    if objItem.PathName != None:
        print("PathName: %s" % objItem.PathName)
    if objItem.ProcessId != None:
        print("ProcessId: %s" % objItem.ProcessId)
    if objItem.ServiceSpecificExitCode != None:
        print("ServiceSpecificExitCode: %s" % objItem.ServiceSpecificExitCode)
    if objItem.ServiceType != None:
        print("ServiceType: %s" % objItem.ServiceType)
    if objItem.Started != None:
        print("Started: %s" % objItem.Started)
    if objItem.StartMode != None:
        print("StartMode: %s" % objItem.StartMode)
    if objItem.StartName != None:
        print("StartName: %s" % objItem.StartName)
    if objItem.State != None:
        print("State: %s" % objItem.State)
    if objItem.Status != None:
        print("Status: %s" % objItem.Status)
    if objItem.SystemCreationClassName != None:
        print("SystemCreationClassName: %s" % objItem.SystemCreationClassName)
    if objItem.SystemName != None:
        print("SystemName: %s" % objItem.SystemName)
    if objItem.TagId != None:
        print("TagId: %s" % objItem.TagId)
    if objItem.WaitHint != None:
        print("WaitHint: %s" % objItem.WaitHint)
