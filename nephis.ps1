# ==============================================================================
# nephis.ps1 - PowerShell launcher for Sunless
# ==============================================================================
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
cmd /c "start.bat" $args
