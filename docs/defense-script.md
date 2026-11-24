# Defense script

Mini Greenhouse Assistant · Miras Yessenaly · individual project

Total talk time: about 8 minutes, then up to 3 minutes of Q&A.
Questions and answers are in [defense-cheatsheet.md](defense-cheatsheet.md).

Pace: the English text is about 5.5 minutes of speech at a calm 130 words per minute. The rest of each slot is for clicking and pausing. If you run late, skip the optional log step in Beat 2.2.

The site is one page. From top to bottom: the question "Did the sensor beep?" with the buttons "Yes, it beeped" and "No, it was quiet", the answer card, the section "How it thinks" with three cards (1, 2, 3), the section "How to use", and the closed block "Details for the teacher". The click steps use these names. Rehearse once on the live site the evening before.

> RU: Английский текст — около 5,5 минут речи в спокойном темпе (130 слов в минуту), остальное время — клики и паузы. Если не успеваешь, пропусти необязательный шаг с логом в Beat 2.2. Сайт — одна страница: вопрос «Did the sensor beep?» с двумя кнопками, карточка ответа, раздел «How it thinks» с тремя карточками, «How to use» и свёрнутый блок «Details for the teacher». Названия в шагах совпадают с сайтом. Вечером перед защитой один раз прогони сценарий на живом сайте.

| Part | Time | Goal |
|---|---|---|
| 1. Problem and goals | 0:00–2:00 | Why noisy sensors are a problem, what the assistant does |
| 2. Live demo | 2:00–6:00 | Show the chain working on the website |
| 3. Three AI topics | 6:00–8:00 | Explain each algorithm in one plain sentence |
| Q&A | 8:00–11:00 | Use the cheatsheet |

Live site: https://greenhouse-ai-blue.vercel.app
Local backup: http://localhost:8000 (after `make dev`)
GitHub: https://github.com/lordwateroff/greenhouse-ai

Every number below comes from the real program output. All model numbers are hypothetical assumptions, which the course allows.

---

## Pre-defense checklist

Do this 15 minutes before your turn.

- [ ] Laptop charged above 80 %, charger in the bag.
- [ ] Do Not Disturb on (Control Center → Focus → Do Not Disturb). Close Telegram, mail and other apps that pop up.
- [ ] Open the live site https://greenhouse-ai-blue.vercel.app in the browser. Click "No, it was quiet" and "Yes, it beeped" once, so the server is warm.
- [ ] Open the local backup in a second tab. In Terminal, from the project folder:
  ```
  make dev
  ```
  Then open http://localhost:8000. It works without internet. If `make` is missing, run `.venv/bin/python -m uvicorn app:app --port 8000` instead.
- [ ] Open a second Terminal tab with the CLI ready:
  ```
  .venv/bin/python -m greenhouse.cli
  ```
- [ ] Run the tests once, so you know they are green:
  ```
  .venv/bin/python -m pytest -q
  ```
  Expected: `41 passed`.
- [ ] Open the slides (docs/presentation.pdf) and the cheatsheet in another window.
- [ ] Browser zoom at 110–125 % so the back row can read the numbers. Hide bookmarks bar.
- [ ] Open the code editor with `greenhouse/bayes.py`, `greenhouse/mdp.py`, `greenhouse/hill_climbing.py` in tabs, in case the teacher says "show me in code".

> RU: За 15 минут до выступления: зарядка, «Не беспокоить», открыть живой сайт и прокликать обе кнопки (Yes / No) (чтобы сервер «проснулся»), запустить `make dev` для запасной локальной версии, открыть терминал с CLI, прогнать тесты (должно быть `41 passed`), открыть слайды, шпаргалку и файлы кода.

---

## Part 1. Problem and goals (0:00–2:00)

### Beat 1.1 · 0:00–0:25

| | |
|---|---|
| Click | The page is open at the top. "Yes, it beeped" is selected. The green answer card shows "Water 30 ml now." |
| Say (EN) | Hello. My name is Miras Yessenaly. My project is the Mini Greenhouse Assistant. It decides when to water a plant and how much, even when the soil sensor is unreliable. |

> RU: Здравствуйте. Меня зовут Мирас Есеналы. Мой проект — Mini Greenhouse Assistant. Он решает, когда поливать растение и сколько, даже если датчик почвы ненадёжный.

### Beat 1.2 · 0:25–1:05

| | |
|---|---|
| Click | Nothing. Look at the audience. |
| Say (EN) | Soil moisture sensors are cheap and noisy. Sometimes they say "dry" when the soil is fine. If we trust them blindly, we either water too much, so roots rot and water is wasted, or we water too little and the plant suffers. |

> RU: Датчики влажности дешёвые и шумные. Иногда они говорят «сухо», когда почва в норме. Если верить им вслепую, мы либо переливаем (гниют корни, тратится вода), либо недоливаем, и растение страдает.

### Beat 1.3 · 1:05–2:00

| | |
|---|---|
| Click | Scroll to "How it thinks". Point at the three cards: 1 Is the soil really dry? → 2 Water now or wait? → 3 How much water? |
| Say (EN) | My goal was to combine three AI topics into one chain. First, Bayes decides how much to trust the sensor. Second, an MDP decides: water now or wait. Third, hill climbing finds the best dose. The output of each step is the input of the next one. All numbers are hypothetical assumptions, and the site lists them under "Details for the teacher". |

> RU: Цель — объединить три темы курса в одну цепочку. Сначала Байес решает, насколько верить датчику. Потом MDP решает: поливать сейчас или ждать. Потом hill climbing подбирает лучшую дозу. Выход каждого шага — вход следующего. Все числа — допущения, на сайте они перечислены в блоке «Details for the teacher».

---

## Part 2. Live demo (2:00–6:00)

### Beat 2.1 · 2:00–2:35 · The main switch

| | |
|---|---|
| Click | Scroll back to the top. "Yes, it beeped" is selected. The green card says "Water 30 ml now." and "I am 66% sure the soil is dry". Click "No, it was quiet". The card turns white with a clock: "Wait. Check again later." and "I am only 5% sure". Click "Yes, it beeped" again. |
| Say (EN) | Here is the whole system on one screen. The sensor says "alert". We are 65.9 % sure the soil is dry, so the assistant says: water 30 ml now. Now I switch to "no alert". The chance of dry soil falls to 5.1 %, and the decision flips to wait. One input changes, and the whole chain reacts. |

> RU: Вся система на одном экране. Датчик говорит «тревога». Мы на 65,9 % уверены, что почва сухая, поэтому помощник говорит: полить 30 мл сейчас. Переключаю на «нет тревоги». Вероятность сухой почвы падает до 5,1 %, и решение меняется на «ждать». Меняем один вход — реагирует вся цепочка.

### Beat 2.2 · 2:35–3:30 · Card 1, Is the soil really dry? (Bayes)

| | |
|---|---|
| Click | Scroll to "How it thinks". Point at card 1: the bars Dry 66% and Fine 34%. |
| Say (EN) | This is step one, Bayes. Input: the prior is 30 % dry, the sensor catches dry soil 90 % of the time, and gives a false alarm 20 % of the time. The steps: P(alert) is 0.27 plus 0.14, which is 0.41. Then 0.27 divided by 0.41 is 0.6585. So the sensor catches 90 % of dry soil, but after an alert we are only 66 % sure. That is because dry soil is less common than normal soil, and false alarms happen 20 % of the time. |

> RU: Шаг один, Байес. Вход: априорная вероятность сухой почвы 30 %, датчик ловит сухую почву в 90 % случаев и даёт ложную тревогу в 20 %. Шаги: P(alert) = 0,27 + 0,14 = 0,41. Потом 0,27 / 0,41 = 0,6585. Датчик ловит 90 % сухой почвы, но после тревоги мы уверены только на 66 %, потому что сухая почва встречается реже нормальной, а ложные тревоги бывают в 20 % случаев.

Optional, if time allows (10 s): open "Details for the teacher" and point at the first lines of "What the code did": P(alert) = 0.2700 + 0.1400 = 0.4100, then P(Dry|alert) = 0.2700 / 0.4100 = 0.6585. Close the block.

> RU: Если есть время: открыть «Details for the teacher» и показать первые строки лога «What the code did»: P(alert) = 0,41, потом 0,27 / 0,41 = 0,6585. Закрыть блок.

### Beat 2.3 · 3:30–4:30 · Card 2, Water now or wait? (MDP)

| | |
|---|---|
| Click | Point at card 2: Water 49.7, Wait 42.8. The longer bar wins. Then open "Details for the teacher": point at "Water wins when P(Dry) is above 37.6%" and at the log line "converged after 148 iterations". Close the block. |
| Say (EN) | Step two is the MDP. Two states, Dry and Normal. Two actions, Water and Wait. Each action has a reward now and a chance to change the soil later. Value iteration repeats the Bellman update until the values stop changing. Here it converges after 148 iterations. The policy is: if dry, water. If normal, wait. But we don't know the state for sure. We only have 66 %. So we weigh both. Watering scores about 49.7, waiting about 42.8. Water wins. The break-even point is 0.376. We water when we are more than 38 % sure the soil is dry. |

> RU: Шаг два, MDP. Два состояния: Dry и Normal. Два действия: Water и Wait. У каждого действия есть награда сейчас и шанс изменить почву потом. Value iteration повторяет обновление Беллмана, пока значения не перестанут меняться — здесь 148 итераций. Политика: сухо — поливать, норма — ждать. Но мы не знаем состояние точно, у нас только 66 %. Поэтому взвешиваем: полив ≈ 49,7, ожидание ≈ 42,8. Побеждает полив. Порог — 0,376: поливаем, когда уверены больше чем на 38 %, что почва сухая.

### Beat 2.4 · 4:30–5:10 · Card 3, How much water? (hill climbing)

| | |
|---|---|
| Click | Point at card 3: five columns for 10 to 50 ml, with 30 ml marked as best. Read the line under them: "Start at 10 ml, then 20, then 30. Best: 30 ml." |
| Say (EN) | Step three is hill climbing. We have five doses, from 10 to 50 ml, each with a plant health score. We start at 10 ml with score 55. The neighbour 20 ml is better, 72, so we move. Then 30 ml, 88. Its neighbours are 72 and 80, both worse, so we stop. Best dose: 30 ml, in two steps. |

> RU: Шаг три, hill climbing. Пять доз от 10 до 50 мл, у каждой оценка здоровья растения. Стартуем с 10 мл, оценка 55. Сосед 20 мл лучше (72) — идём. Потом 30 мл (88). Соседи 72 и 80 хуже — стоп. Лучшая доза 30 мл за два шага.

### Beat 2.5 · 5:10–6:00 · Tricky plant and restarts

| | |
|---|---|
| Click | Open "Details for the teacher". Tick "Tricky plant". Card 3 now says "Stuck at 20 ml, but 40 ml is better. A small hill fooled it." Tick "Try every start". Card 3 says "I tried every start. Best: 40 ml." and the answer card says "Water 40 ml now." Untick both boxes. |
| Say (EN) | Hill climbing has a weak spot. With the tricky plant, from 10 ml it climbs to 20 ml and gets stuck, because both neighbours are worse. But the real best is 40 ml, score 85. This is a local maximum. The fix is restarts: we climb again from each of the five doses and keep the best top. Now we get 40 ml. |

> RU: У hill climbing есть слабое место. С «трудным растением» (tricky plant) с 10 мл алгоритм доходит до 20 мл и застревает: оба соседа хуже. А лучшая доза — 40 мл, оценка 85. Это локальный максимум. Исправление — перезапуски: запускаем подъём с каждой из пяти доз и берём лучшую вершину. Получаем 40 мл.

Honest note if asked: our "random restart" is deterministic. It restarts from every one of the 5 doses, not from random ones. With 5 doses, trying all of them is cheaper and always finds the best top.

> RU: Если спросят: наш «random restart» на самом деле детерминированный — перезапуск с каждой из 5 доз, а не со случайных. При 5 дозах перебрать все дешевле, и это всегда находит лучшую вершину.

---

## Part 3. Three AI topics (6:00–8:00)

### Beat 3.1 · 6:00–6:30 · Probabilistic reasoning

| | |
|---|---|
| Click | Slide 4, or card 1 on the site with the Dry and Fine bars. |
| Say (EN) | Topic one is probabilistic reasoning, Bayes. The sensor says 'dry', but it sometimes lies. Bayes tells us how much to trust it. It combines the prior, how common dry soil is, with the likelihood, how good the sensor is. The result, the posterior, goes into the MDP as our belief. |

> RU: Тема один — вероятностные рассуждения, Байес. «Датчик кричит "сухо", но иногда врёт. Байес говорит, насколько ему верить». Он объединяет prior (как часто почва сухая) и likelihood (насколько хорош датчик). Результат, posterior, идёт в MDP как наша уверенность.

### Beat 3.2 · 6:30–7:10 · Sequential decision making

| | |
|---|---|
| Click | Slide 5, or card 2 on the site with the Water and Wait bars. |
| Say (EN) | Topic two is sequential decision making, the MDP. For each action we ask: what do I get now, plus what can I expect later? We pick the bigger number. Gamma 0.9 means future rewards count a bit less than rewards now. Because we only have a belief, we weigh the Q values by P(Dry). This is a simplification called QMDP. A full POMDP is future work. |

> RU: Тема два — последовательное принятие решений, MDP. «Для каждого действия считаем: что получим сейчас плюс что ждёт потом. Выбираем, где больше». Gamma 0,9 значит, что будущие награды весят чуть меньше, чем текущие. Так как у нас только вероятность, мы взвешиваем Q по P(Dry). Это упрощение, QMDP. Полный POMDP — на будущее.

### Beat 3.3 · 7:10–8:00 · Local search, and wrap-up

| | |
|---|---|
| Click | Slide 7 with the results, or the Terminal tab: run `.venv/bin/python -m pytest -q` and show `41 passed`. |
| Say (EN) | Topic three is local search, hill climbing. Try a bit more or a bit less water. If the plant gets better, keep going that way. If it gets worse, stop. Together the three answer one question: should I water this plant now, and how much? The results table shows the same code on different inputs. For example, when dry soil is rare, with a prior of 10 %, the assistant waits even on an alert. The project has 41 automated tests that check the hand-calculated numbers. Thank you. I'm ready for questions. |

> RU: Тема три — локальный поиск, hill climbing. «Пробуем полить чуть больше или чуть меньше. Если лучше, идём дальше. Если хуже, стоп». Вместе три алгоритма отвечают на один вопрос: поливать ли растение сейчас и сколько. Таблица результатов показывает тот же код на других входах: например, когда сухая почва редкая (prior 10 %), помощник ждёт даже при тревоге. В проекте 41 автотест, они проверяют числа, посчитанные вручную. Спасибо, готов ответить на вопросы.

The example in the results table: prior 0.1 and false alarm 0.2 give P(Dry|alert) = 0.3333, which is below 0.376, so the action is Wait.

> RU: Пример из таблицы: prior 0,1 и ложная тревога 0,2 дают P(Dry|alert) = 0,3333, это меньше 0,376, поэтому Wait.

---

## Fallback if Wi-Fi or the live site fails

Stay calm. Say one sentence and switch.

> Say (EN): The network is slow, so I'll use the local version. It runs the same code.
>
> RU: Сеть медленная, поэтому покажу локальную версию. Там тот же код.

1. Switch to the tab http://localhost:8000 (started with `make dev`). The site is the same and runs offline.
2. If the browser also fails, switch to the Terminal tab and run the CLI. It prints the input, the steps and the output of all three algorithms:
   ```
   .venv/bin/python -m greenhouse.cli                      # alert: Water 30 ml now
   .venv/bin/python -m greenhouse.cli no_alert             # Wait. Check again later
   .venv/bin/python -m greenhouse.cli --tricky             # stuck at 20 ml: Water 20 ml now
   .venv/bin/python -m greenhouse.cli --tricky --restarts  # restarts find 40 ml
   .venv/bin/python -m greenhouse.experiments              # results tables
   .venv/bin/python -m pytest -q                           # 41 passed
   ```
3. If the laptop fails completely, use the slides (docs/presentation.pdf) on another computer and talk through the same numbers.

> RU: Если Wi-Fi или сайт не работают: (1) вкладка http://localhost:8000 (`make dev`), там тот же сайт; (2) если и браузер не работает — терминал и CLI, он печатает всё: вход → шаги → выход; (3) если ноутбук совсем сломался — слайды на другом компьютере.

## Numbers to remember

| What | Value |
|---|---|
| P(alert) | 0.27 + 0.14 = 0.41 |
| P(Dry \| alert) | 0.6585 (65.9 %) |
| P(Dry \| no alert) | 0.03 / 0.59 = 0.0508 (5.1 %) |
| Value iteration | V1 = (6, 5), converges in 148 iterations |
| V*(Dry), V*(Normal) | 53.1356, 52.2881 |
| Policy | Dry → Water, Normal → Wait |
| Alert scores | Water ≈ 49.7, Wait ≈ 42.8 (42.76 in the Steps log) → Water |
| No alert scores | Water 43.57, Wait 51.55 → Wait |
| Threshold | water when P(Dry) > 0.376 (about 38 %) |
| Hill climbing | 10 → 20 → 30, best 30 ml, score 88, 2 steps |
| Tricky plant | stuck at 20 ml (70); every start gives 40 ml (85) |
| Tests | 41 passing |
