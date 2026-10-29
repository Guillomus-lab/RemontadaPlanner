' Launches Remontada Planner with no console window.
' Uses the BASE interpreter's pythonw.exe (read from .venv\pyvenv.cfg): the uv venv's
' own pythonw.exe is a trampoline that starts console python.exe, which either shows a
' black console or, when launched hidden, keeps the app window hidden as well.
' app.pyw adds the venv's site-packages itself.
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
appFile = scriptDir & "\app.pyw"
pyExe = scriptDir & "\.venv\Scripts\pythonw.exe"

cfgPath = scriptDir & "\.venv\pyvenv.cfg"
If FSO.FileExists(cfgPath) Then
  Set cfg = FSO.OpenTextFile(cfgPath, 1)
  Do Until cfg.AtEndOfStream
    line = cfg.ReadLine
    If LCase(Trim(Left(line, InStr(line & "=", "=") - 1))) = "home" Then
      candidate = Trim(Mid(line, InStr(line, "=") + 1)) & "\pythonw.exe"
      If FSO.FileExists(candidate) Then pyExe = candidate
    End If
  Loop
  cfg.Close
End If

WshShell.CurrentDirectory = scriptDir
' 1 = normal window: pythonw.exe has no console, so nothing else appears
WshShell.Run Chr(34) & pyExe & Chr(34) & " " & Chr(34) & appFile & Chr(34), 1, False
