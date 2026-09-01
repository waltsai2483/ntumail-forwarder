# NTUMail 自動轉寄

## 功能

透過 Github Action 每十分鐘將新郵件從 NTUMail 轉寄到指定信箱。

## 設定

1. 複製此 Template
2. Settings => Secrets & Variables => Actions
3. 新增三個 Secrets，可防止帳密外洩
    - `NTUMAIL_ADDRESS`: 你的 NTUMail 信箱 (...@ntu.edu.tw)
    - `NTUMAIL_PASSWORD`: 你的密碼
    - `FORWARDING_ADDRESSES`: 目標轉寄信箱，超過一個則用 `, ` 隔開

注意在啟動此功能前，原有的郵件不會被轉寄至其他信箱。