$cwd = Get-Location
Set-Location -Path D:\Code\mame\

workflow Start-Mame {
    param ([int] $numInstances)

    foreach -parallel ($i in 1..$numInstances) {
        $mameID = Start-Process -FilePath "mame64.exe" -ArgumentList ("vsav", "-autoboot_script", "zmq_dealerclient_msgpack.lua") -PassThru
        Start-Sleep -s 60
        Get-Process -Id $mameID.id | Stop-Process
    }

}

$numInstances = 2
Write-Output "Launching $numInstances instances of MAME"
Start-Mame -numInstances $numInstances
Set-Location -Path $cwd
