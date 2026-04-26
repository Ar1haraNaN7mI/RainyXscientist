param(
    [string]$Token = $env:Rxsci_MOBILE_TOKEN,
    [string]$Workdir = (Get-Location).Path,
    [int]$Port = 8765,
    [string]$HostAddress = "0.0.0.0",
    [switch]$AutoApprove,
    [switch]$NoThinking,
    [switch]$Debug
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "Mobile token is required. Pass -Token or set Rxsci_MOBILE_TOKEN."
}

rxsci config set channel_enabled mobile
rxsci config set mobile_host $HostAddress
rxsci config set mobile_port $Port
rxsci config set mobile_token $Token
rxsci config set channel_send_thinking true

$argsList = @("serve", "--workdir", $Workdir)
if ($AutoApprove) { $argsList += "--auto-approve" }
if ($NoThinking) { $argsList += "--no-thinking" }
if ($Debug) { $argsList += "--debug" }

rxsci @argsList
