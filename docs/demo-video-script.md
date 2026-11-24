# Demo video script

Mini Greenhouse Assistant · about 2 min 50 s · screen recording with voice

Record the live site https://greenhouse-ai-blue.vercel.app, or the local version at http://localhost:8000 after `make dev`. Both run the same code.

> RU: Цель — ролик около 2:50. Записывай живой сайт или локальную версию (`make dev`), код одинаковый. Говори медленно, лучше короче, чем быстрее.

## Shot list and narration

| Time | Shot (what is on screen) | Narration (EN) |
|---|---|---|
| 0:00–0:15 | Top of the page. "Yes, it beeped" is selected. The green answer card with the measuring cup says "Water 30 ml now." | This is the Mini Greenhouse Assistant. It decides when to water a plant and how much, even when the soil sensor is unreliable. |
| 0:15–0:35 | Scroll down to "How it thinks". Slowly move the cursor over the three cards: 1 Is the soil really dry? → 2 Water now or wait? → 3 How much water? Scroll back to the top. | Cheap soil sensors are noisy. So the assistant uses three AI algorithms in one chain. Bayes weighs the sensor. An MDP decides to water or wait. Hill climbing picks the dose. All numbers are hypothetical assumptions. |
| 0:35–0:55 | Click "No, it was quiet". The card turns white with a clock: "Wait. Check again later." Click "Yes, it beeped" again. | When the sensor gives no alert, the chance of dry soil drops to 5.1 %, and the decision flips to wait. With an alert, it goes back to water 30 ml. |
| 0:55–1:25 | Scroll to "How it thinks". Point at card 1: Dry 66%, Fine 34%. | The sensor says 'dry', but it sometimes lies. Bayes tells us how much to trust it. The prior is 30 %. The sensor catches dry soil 90 % of the time, with 20 % false alarms. P(alert) is 0.41, so P(Dry) is 0.27 divided by 0.41, about 66 %. |
| 1:25–1:55 | Point at card 2: Water 49.7, Wait 42.8. Open "Details for the teacher" and point at "Water wins when P(Dry) is above 37.6%" and the log line "converged after 148 iterations". | For each action we ask: what do I get now, plus what can I expect later? We pick the bigger number. Value iteration converges in 148 iterations. Weighted by our 66 % belief, watering scores about 49.7 and waiting about 42.8. We water when we are more than 38 % sure the soil is dry. |
| 1:55–2:20 | Point at card 3: five dose columns, 30 ml marked best. The line under them says "Start at 10 ml, then 20, then 30. Best: 30 ml." | Try a bit more or a bit less water. If the plant gets better, keep going that way. If it gets worse, stop. From 10 ml we climb to 30 ml, score 88, in two steps. |
| 2:20–2:40 | In "Details for the teacher", tick "Tricky plant". Card 3 says "Stuck at 20 ml, but 40 ml is better. A small hill fooled it." Tick "Try every start". Card 3 says "I tried every start. Best: 40 ml." and the answer card says "Water 40 ml now." | With tricky scores, the climb gets stuck at 20 ml. That is a local maximum. We restart from each of the five doses and keep the best top, 40 ml. |
| 2:40–2:50 | Cut to a terminal with `.venv/bin/python -m pytest -q` showing `41 passed`. Then click "Code" at the top of the page to show the GitHub repo. | 41 automated tests check the results. The code is on GitHub. Thank you for watching. |

> RU (заметки):
> - 0:00–0:35 — вступление и цепочка. Не торопись, это главное.
> - 0:35–0:55 — ключевой момент: кнопки «Yes, it beeped» / «No, it was quiet» меняют решение. Сделай паузу 1–2 секунды после клика, чтобы было видно смену карточки.
> - 0:55–2:20 — по одной карточке на алгоритм в разделе «How it thinks», плюс блок «Details for the teacher».
> - 2:20–2:40 — галочки «Tricky plant» и «Try every start». Если спросят: перезапуск идёт с каждой из 5 доз, а не случайно.
> - 2:40–2:50 — тесты и GitHub, конец.

## Before recording

- Do Not Disturb on, close Telegram and mail. Hide the Dock (System Settings → Desktop & Dock → Automatically hide).
- Browser full screen, zoom 110–125 %, bookmarks bar hidden. One tab only.
- Click "No, it was quiet" and "Yes, it beeped" once first, so the server is warm and the first frame shows "Water 30 ml now."
- Make sure "Tricky plant" and "Try every start" are unticked and "Details for the teacher" is closed. Reloading the page resets everything.
- Use earphones with a mic or the MacBook mic in a quiet room. Do one 10-second test recording and listen to it.

> RU: Перед записью: «Не беспокоить», закрыть мессенджеры, скрыть Dock, браузер на весь экран, зум 110–125 %. Один раз прокликать обе кнопки (Yes / No), проверить, что галочки «Tricky plant» и «Try every start» сняты, а «Details for the teacher» свёрнут. Перезагрузка страницы всё сбрасывает. Записать 10 секунд пробы и послушать звук.

## How to record on a Mac

Option A, the Screenshot toolbar (simplest):

1. Press Cmd+Shift+5.
2. Choose "Record Selected Portion" (the icon with a dotted rectangle and a circle). Drag the frame over the browser window.
3. Click Options → Microphone → choose your mic (for example "MacBook Pro Microphone"). Also choose Save to → Desktop. Turn on "Show Mouse Clicks" if you want.
4. Click Record. Read the narration and follow the shot list.
5. To stop, click the stop button in the menu bar, or press Cmd+Control+Esc.
6. The file appears on the Desktop as a .mov.

Option B, QuickTime Player:

1. Open QuickTime Player → File → New Screen Recording. The same toolbar opens.
2. Choose Options → Microphone, then "Record Selected Portion", then Record.
3. Stop from the menu bar. QuickTime opens the video. File → Save.

> RU: Запись: Cmd+Shift+5 → «Записать выбранную область» → Параметры → Микрофон (выбрать свой) → Сохранить на «Рабочий стол» → Запись. Остановить — кнопка в строке меню или Cmd+Control+Esc. Либо QuickTime Player → Файл → Новая запись экрана. Если ошибся — не страшно, остановись и запиши заново, ролик короткий.

## Edit and export

1. Open the .mov in QuickTime Player.
2. Edit → Trim (Cmd+T) to cut silence at the start and the end. Keep it 2–3 minutes.
3. File → Export As → 1080p. This makes a smaller file that uploads faster.
4. Name it `greenhouse-demo.mov`.

> RU: QuickTime → Правка → Обрезать (Cmd+T) — убрать тишину в начале и в конце. Файл → Экспортировать как → 1080p. Назвать `greenhouse-demo.mov`.

## Upload

Option 1, YouTube (unlisted):

1. youtube.com → Create → Upload video → choose the file.
2. Title: "Mini Greenhouse Assistant: AI Fundamentals final project".
3. Audience: "No, it's not made for kids".
4. Visibility: Unlisted. Click Save and copy the link.

Option 2, Google Drive:

1. drive.google.com → New → File upload → choose the file.
2. Right-click the file → Share → General access: "Anyone with the link" (Viewer). Copy link.
3. Open the link in a private window to check it plays without logging in.

> RU: YouTube: Создать → Загрузить видео → доступ «По ссылке» (Unlisted) → скопировать ссылку. Или Google Drive: Загрузить файл → Поделиться → «Все, у кого есть ссылка» (читатель) → скопировать ссылку. Обязательно проверь ссылку в режиме инкогнито.

## Where to paste the link

1. README.md, section Docs: add a line like `- Demo video: <link>`.
2. The course submission form, in the field for the demo video.
3. Optional: the last slide of the presentation, next to the live demo link.

After you edit the README, commit and push it.

> RU: Ссылку вставить: (1) в README.md, раздел Docs, строкой `- Demo video: <ссылка>`; (2) в форму сдачи курса; (3) по желанию на последний слайд. После правки README сделать коммит и push.
