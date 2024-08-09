BACK_TO_HOME_PAGE_TEXT = "العودة إلى القائمة الرئيسية🔙"
BACK_TEXT = "الرجوع 🔙"
HOME_PAGE_TEXT = "القائمة الرئيسية 🔝"

SOLANA_ADDRESS_PATTERN = r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"
SOLANA_SA_ADDRESS_PATTERN = rf"(?<!https://dexscreener\.com/solana/){SOLANA_ADDRESS_PATTERN}"
SOLANA_LINK_PATTERN = r"https://dexscreener\.com/solana/[0-9A-Za-z]{32,44}"

ETH_ADDRESS_PATTERN = r"^0x[0-9a-fA-F]{40}$"
ETH_SA_ADDRESS_PATTERN = rf"(?<!https://dexscreener\.com/ethereum/){ETH_ADDRESS_PATTERN}"
ETH_LINK_PATTERN = r"https://dexscreener\.com/ethereum/0x[0-9a-fA-F]{40}"