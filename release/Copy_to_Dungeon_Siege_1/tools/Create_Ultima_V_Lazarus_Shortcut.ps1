[CmdletBinding()]
param(
    [string]$GameDirectory,
    [string]$ShortcutDirectory
)

$ErrorActionPreference = 'Stop'

function Test-DungeonSiegeDirectory {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $false
    }
    return Test-Path -LiteralPath (Join-Path $Path 'DungeonSiege.exe') -PathType Leaf
}

try {
    $packageDirectory = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
    $candidates = @(
        $GameDirectory
        'C:\Games\Steam\steamapps\common\Dungeon Siege 1'
        (Join-Path ${env:ProgramFiles(x86)} 'Steam\steamapps\common\Dungeon Siege 1')
        (Join-Path $env:ProgramFiles 'Steam\steamapps\common\Dungeon Siege 1')
        $packageDirectory
    )

    $selectedDirectory = $candidates |
        Where-Object { Test-DungeonSiegeDirectory $_ } |
        Select-Object -First 1

    if (-not $selectedDirectory) {
        Add-Type -AssemblyName System.Windows.Forms
        $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description = 'DungeonSiege.exe가 있는 Dungeon Siege 1 폴더를 선택하세요.'
        $dialog.ShowNewFolderButton = $false
        if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
            Write-Host '취소했습니다.'
            exit 1
        }
        $selectedDirectory = $dialog.SelectedPath
    }

    $gameDirectoryPath = [System.IO.Path]::GetFullPath($selectedDirectory)
    $executable = Join-Path $gameDirectoryPath 'DungeonSiege.exe'
    $resources = Join-Path $gameDirectoryPath 'Resources'
    $lazarusLogic = Join-Path $resources 'lazarus_logic.dsres'
    $lazarusArt = Join-Path $resources 'lazarus_art.dsres'

    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        throw "DungeonSiege.exe를 찾을 수 없습니다: $executable"
    }
    if (-not (Test-Path -LiteralPath $lazarusLogic -PathType Leaf)) {
        throw "lazarus_logic.dsres를 찾을 수 없습니다: $lazarusLogic"
    }
    if (-not (Test-Path -LiteralPath $lazarusArt -PathType Leaf)) {
        throw "lazarus_art.dsres를 찾을 수 없습니다: $lazarusArt"
    }

    $desktop = if ([string]::IsNullOrWhiteSpace($ShortcutDirectory)) {
        [Environment]::GetFolderPath('Desktop')
    }
    else {
        [System.IO.Path]::GetFullPath($ShortcutDirectory)
    }
    if (-not (Test-Path -LiteralPath $desktop -PathType Container)) {
        New-Item -ItemType Directory -Path $desktop | Out-Null
    }
    $shortcutPath = Join-Path $desktop 'Ultima V - Lazarus v1.20.lnk'
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $executable
    $shortcut.Arguments = ('map_paths=!"{0}" res_paths="{0}"' -f $resources)
    $shortcut.WorkingDirectory = $gameDirectoryPath
    $shortcut.Description = 'Ultima V: Lazarus v1.20'

    $icon = Join-Path $gameDirectoryPath 'U5.ico'
    if (Test-Path -LiteralPath $icon -PathType Leaf) {
        $shortcut.IconLocation = "$icon,0"
    }
    else {
        $shortcut.IconLocation = "$executable,0"
    }
    $shortcut.Save()

    Write-Host 'Ultima V: Lazarus 바로가기를 만들었습니다.'
    Write-Host "위치: $shortcutPath"
    Write-Host "대상: $executable"
    Write-Host "시작 위치: $gameDirectoryPath"
}
catch {
    Write-Error $_
    exit 1
}
