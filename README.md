## Start tg bot

Сначала нужно указать TELEGRAM_API_ID, TELEGRAM_API_HASH и BOT_TOKEN в docker-compose.yml

Затем экспортировать cookies для логина на youtube (инструкция ниже)

После настройки, бот запускается через docker compose up


## Exporting YouTube cookies

> [!CAUTION]
> By using your account with yt-dlp, you run the risk of it being banned (temporarily or permanently).
> Be mindful with the request rate and amount of downloads you make with an account. Use it only when necessary, or consider using a throwaway account.

> [!NOTE]
> This is only necessary for content that requires an account to access, such as private playlists, age-restricted videos and members-only content.

> [!NOTE]
> You may use a conforming browser extension for exporting cookies, such as [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) for Chrome or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) for Firefox. As with any browser extension, be careful about what you install. If you had previously installed the "Get cookies.txt" (not "LOCALLY") Chrome extension, it's recommended to uninstall it immediately; it has been reported as malware and removed from the Chrome Web Store.
>
> Note that the cookies file must be in Mozilla/Netscape format and the first line of the cookies file must be either # HTTP Cookie File or # Netscape HTTP Cookie File. Make sure you have correct newline format in the cookies file and convert newlines if necessary to correspond with your OS, namely CRLF (\r\n) for Windows and LF (\n) for Unix and Unix-like systems (Linux, macOS, etc.). HTTP Error 400: Bad Request when using --cookies is a good sign of invalid newline format.

YouTube rotates account cookies frequently on open YouTube browser tabs as a security measure.
To export cookies that will remain working with yt-dlp, you will need to export cookies in such a way that they are never rotated. 

One way to do this is through a private browsing/incognito window:
1. Open a new private browsing/incognito window and log into YouTube
2. In same window and same tab from step 1, navigate to `https://www.youtube.com/robots.txt` (this should be the **only** private/incognito browsing tab open)
3. Export `youtube.com` cookies from the browser, then **close the private browsing/incognito window** so that the session is never opened in the browser again.

> [!NOTE]
> Do **NOT** use the `--cookies COOKIEFILE --cookies-from-browser BROWSER` method (as described in the above FAQ link) to export your cookies to a cookiefile. This will export **all** of your regular browser cookies, but **not** the cookies from this private/incognito YouTube session. Instead, use one of the browser extensions recommended in the [FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp).
