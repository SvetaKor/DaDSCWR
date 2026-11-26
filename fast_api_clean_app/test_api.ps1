$BaseUrl = "http://localhost:8000"
$ErrorActionPreference = "Stop"

function Show-Result($label, $status) {
    Write-Host "[$label] HTTP $status" -ForegroundColor Cyan
}

# --- Регистрация ---
$body = @{
    email        = "alice@test.com"
    password     = "Pass1234"
    display_name = "Alice"
} | ConvertTo-Json

try {
    $reg = Invoke-RestMethod -Uri "$BaseUrl/auth/register" -Method Post `
        -ContentType "application/json" -Body $body
    Show-Result "register" 201
    $access  = $reg.access_token
    $refresh = $reg.refresh_token
} catch {
    Show-Result "register" $_.Exception.Response.StatusCode.value__
    throw
}

# --- Дубликат email ---
try {
    Invoke-RestMethod -Uri "$BaseUrl/auth/register" -Method Post `
        -ContentType "application/json" -Body $body
} catch {
    Show-Result "register duplicate" $_.Exception.Response.StatusCode.value__  # 409
}

# --- Логин ---
$loginBody = @{ email = "alice@test.com"; password = "Pass1234" } | ConvertTo-Json
$login = Invoke-RestMethod -Uri "$BaseUrl/auth/login" -Method Post `
    -ContentType "application/json" -Body $loginBody
Show-Result "login" 200

# --- /me ---
$headers = @{ Authorization = "Bearer $($login.access_token)" }
$me = Invoke-RestMethod -Uri "$BaseUrl/auth/me" -Method Get -Headers $headers
Show-Result "me" 200
$me | ConvertTo-Json

# --- Refresh ---
$refreshBody = @{ refresh_token = $login.refresh_token } | ConvertTo-Json
$new = Invoke-RestMethod -Uri "$BaseUrl/auth/refresh" -Method Post `
    -ContentType "application/json" -Body $refreshBody
Show-Result "refresh" 200

# --- Reuse detection ---
try {
    Invoke-RestMethod -Uri "$BaseUrl/auth/refresh" -Method Post `
        -ContentType "application/json" -Body $refreshBody
} catch {
    Show-Result "reuse detection" $_.Exception.Response.StatusCode.value__  # 401
}

Write-Host "All checks done." -ForegroundColor Green
