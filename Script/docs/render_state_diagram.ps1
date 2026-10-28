# Windows 기본 그리기 기능과 맑은 고딕으로 한국어 상태 다이어그램을 생성한다.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$bitmap = New-Object System.Drawing.Bitmap(2200, 1550)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$graphics.Clear([System.Drawing.Color]::FromArgb(247, 249, 252))
$titleFont = New-Object System.Drawing.Font('Malgun Gothic', 46, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$nodeFont = New-Object System.Drawing.Font('Malgun Gothic', 34, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$bodyFont = New-Object System.Drawing.Font('Malgun Gothic', 24, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$labelFont = New-Object System.Drawing.Font('Malgun Gothic', 25, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$ink = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(30, 45, 65))
$line = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(87, 105, 130), 4)
$arrow = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(5, 6)
$line.CustomEndCap = $arrow
$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center

function Text([string]$value, [float]$x, [float]$y, [float]$w, [float]$h, $font) {
    $rect = New-Object System.Drawing.RectangleF($x, $y, $w, $h)
    $graphics.DrawString($value, $font, $ink, $rect, $format)
}

function Label([string]$value, [float]$x, [float]$y, [float]$w, [float]$h = 65) {
    $graphics.FillRectangle([System.Drawing.Brushes]::White, $x, $y, $w, $h)
    Text $value $x $y $w $h $labelFont
}

function Node([float]$x, [float]$y, [string]$title, [string]$body, [string]$color) {
    $fill = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($color))
    $border = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(190, 203, 220), 2)
    $graphics.FillRectangle($fill, $x, $y, 360, 170)
    $graphics.DrawRectangle($border, $x, $y, 360, 170)
    Text $title $x ($y + 20) 360 55 $nodeFont
    Text $body ($x + 10) ($y + 80) 340 70 $bodyFont
    $fill.Dispose()
    $border.Dispose()
}

try {
    Text '소년 상태 다이어그램' 0 45 2200 75 $titleFont
    Text '입력 처리 → 상태 갱신 → 화면 표시' 0 125 2200 50 $bodyFont

    # 대기 ↔ 수면
    $graphics.DrawBezier($line, 920, 340, 740, 430, 610, 570, 510, 665)
    $graphics.DrawBezier($line, 280, 665, 360, 390, 650, 230, 920, 260)
    # 대기 ↔ 기본 달리기
    $graphics.DrawLine($line, 1030, 385, 1030, 1115)
    $graphics.DrawLine($line, 1170, 1115, 1170, 385)
    # 대기 ↔ 자동 달리기
    $graphics.DrawBezier($line, 1280, 260, 1550, 230, 1830, 390, 1920, 665)
    $graphics.DrawBezier($line, 1690, 665, 1590, 570, 1460, 430, 1280, 340)
    # 수면과 자동 달리기 → 기본 달리기
    $graphics.DrawLine($line, 510, 835, 960, 1115)
    $graphics.DrawLine($line, 1690, 835, 1240, 1115)
    # 자동 달리기 벽 반사: 상태는 유지한다.
    $graphics.DrawBezier($line, 1980, 710, 2180, 580, 2180, 920, 1980, 800)

    Label '5초 대기' 580 490 210
    Label '스페이스 키' 390 310 240
    Label '좌우 키 누름' 785 620 230
    Label "좌우 키 모두`n해제" 1185 840 240 85
    Label 'a 키 누름 · 즉시 시작' 1500 310 340
    Label "5초 경과`n좌우 키 누름 없음" 1380 485 300 90
    Label '좌우 키 누름' 580 950 250
    Label "좌우 키 누름`n시간 만료보다 우선" 1340 950 320 90
    Label "벽에 닿으면`n방향 반전" 1935 525 240 90

    Node 920 215 '대기 (IDLE)' "기본 크기 · 정지`n대기 애니메이션" '#E5EFFC'
    Node 220 665 '수면 (SLEEP)' "잠든 자세`n스페이스 또는 좌우 키로 해제" '#EEE8FC'
    Node 920 1115 '기본 달리기 (RUN)' "속도 200픽셀/초`n기본 크기 100 × 100" '#E5F5ED'
    Node 1620 665 '자동 달리기' "속도 2배 · 크기 1.5배`n오른쪽 시작 · 좌우 왕복" '#FFF0D9'

    Text '자동 달리기: 최대 5초 · 좌우 키만 취소 · 상하 키는 무시' 100 1340 2000 60 $nodeFont
    Text '자동 달리기 종료 시 타이머 해제 · 기본 속도와 크기로 복원' 100 1410 2000 50 $bodyFont
    $outputPath = Join-Path $PSScriptRoot 'state_diagram.png'
    $bitmap.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output $outputPath
}
finally {
    $format.Dispose()
    $arrow.Dispose()
    $line.Dispose()
    $ink.Dispose()
    $titleFont.Dispose()
    $nodeFont.Dispose()
    $bodyFont.Dispose()
    $labelFont.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}
