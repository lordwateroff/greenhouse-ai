# Defense cheatsheet

Mini Greenhouse Assistant · Miras Yessenaly · individual project
Live demo: https://greenhouse-ai-blue.vercel.app · Code: https://github.com/lordwateroff/greenhouse-ai

How to use this file: say the English part out loud. The Russian part in the grey quote is only for you, so you understand what you are saying. All numbers here are copied from the real program output.

---

## If you remember only this

**The chain**

```
Sensor says "dry" (alert)
   → ① Bayes          "Is the soil really dry?"     → P(Dry) = 66%
   → ② MDP            "Water now or wait?"          → Water
   → ③ Hill climbing  "How much water?"             → 30 ml
   → "Water 30 ml now."
```

**Three one-liners**

- **Bayes:** "The sensor says 'dry', but it sometimes lies. Bayes tells us how much to trust it."
- **MDP:** "For each action we ask: what do I get now, plus what can I expect later? We pick the bigger number."
- **Hill climbing:** "Try a bit more or a bit less water. If the plant gets better, keep going that way. If it gets worse, stop."

**Four magic numbers**

| Number | What it means |
|---|---|
| **66%** | After an alert, we are 66% sure the soil is dry (not 90%). |
| **38%** | We water when we are more than 38% sure the soil is dry. |
| **Water** | With 66% we are above 38%, so the decision is Water. |
| **30 ml** | Hill climbing goes 10 → 20 → 30 ml and stops. Best score 88. |

> **По-русски, если помнишь только это.**
> Цепочка: датчик кричит «сухо» → Байес: «правда сухо?» → 66% → MDP: «поливать или ждать?» → поливать → hill climbing: «сколько?» → 30 мл → «Полей 30 мл сейчас».
> - Байес: «Датчик кричит "сухо", но иногда врёт. Байес говорит, насколько ему верить».
> - MDP: «Для каждого действия считаем: что получим сейчас плюс что ждёт потом. Выбираем, где больше».
> - Hill climbing: «Пробуем полить чуть больше или чуть меньше. Если лучше, идём дальше. Если хуже, стоп. Как подбирать громкость музыки».
>
> Четыре числа: **66%** (уверенность, что сухо, после тревоги), **38%** (порог: выше него поливаем), **Water** (66 > 38, значит поливаем), **30 мл** (лучшая доза, оценка 88).

---

## Likely questions

### 1. Why these three algorithms? How do they work together?

**Say:** Our course topic 04 asks for exactly these three, and each one answers a different question. Bayes answers "is the soil really dry?". The MDP answers "should I water now or wait?". Hill climbing answers "how much water?". The output of Bayes, the belief P(Dry), is the input of the MDP decision, and the dose from hill climbing is used only if the MDP says Water.

> Тема 04 в методичке прямо требует эти три алгоритма, и каждый отвечает на свой вопрос: Байес — «правда ли сухо?», MDP — «поливать или ждать?», hill climbing — «сколько воды?». Выход Байеса (вероятность P(Dry)) — это вход для решения MDP. Доза из hill climbing используется, только если MDP сказал «Water». Это и есть интеграция, а не три отдельных алгоритма.

### 2. What are the prior, the likelihood and the posterior?

**Say:** The prior is what we believe before looking at the sensor: the soil is dry 30% of the time. The likelihood is how the sensor behaves: it says "alert" for 90% of dry soil and gives a false alarm 20% of the time on normal soil. The posterior is our updated belief after we see the reading.

> Prior (априорная вероятность) — что мы думаем до показаний датчика: почва сухая в 30% случаев. Likelihood (правдоподобие) — как ведёт себя датчик: ловит сухую почву в 90% случаев и даёт ложную тревогу в 20% случаев на нормальной почве. Posterior (апостериорная) — наша обновлённая уверенность после показаний.

### 3. The sensor is 90% accurate. Why do you get 66% and not 90%?

**Say:** Because dry soil is not common, and false alarms happen often. Imagine 100 days. On 30 dry days the sensor alerts 27 times. On 70 normal days it gives 14 false alarms. So out of 41 alerts only 27 are real, and 27 divided by 41 is 66%. Also, 90% is only how often it catches dry soil. On normal soil it is right 80% of the time.

> Потому что сухая почва сама по себе редкость (30%), а ложные тревоги частые (20%). Представь 100 дней: из 30 сухих датчик сработает 27 раз, из 70 нормальных — 14 раз ложно. Всего 41 тревога, из них настоящих 27. 27 / 41 = 0.6585 ≈ 66%. И ещё: 90% — это только как часто датчик ловит сухую почву; на нормальной он прав в 80% случаев. Формула: P(alert) = 0.9·0.3 + 0.2·0.7 = 0.27 + 0.14 = 0.41; P(Dry|alert) = 0.27 / 0.41.

### 4. What happens when there is no alert?

**Say:** Then we are only 5% sure the soil is dry. Out of 100 days, the sensor stays quiet on 3 dry days and on 56 normal days. So 3 out of 59 quiet days are dry, which is about 5.1%. 5% is far below 38%, so the decision is Wait. The site says "Wait. Check again later." and, below it, "No watering now. When it's needed, the best dose is 30 ml."

> Без тревоги уверенность, что сухо, всего 5%. Из 100 дней датчик молчит в 3 сухих и в 56 нормальных днях. 3 / 59 = 0.0508 ≈ 5.1%. Это сильно меньше 38%, поэтому решение «Wait» (ждать). Счёт: Water = 43.57, Wait = 51.55.

### 5. What is an MDP? What are the states, actions, rewards and transitions in your project?

**Say:** An MDP is a model for making decisions step by step when the result is a bit random. Markov means tomorrow depends only on today's state and action, not on the whole history. Our states are Dry and Normal. Our actions are Water and Wait. Rewards say what we get right now: for example, watering dry soil gives +6, waiting on dry soil gives −10, watering normal soil gives −4, waiting on normal soil gives +5. Transitions say where we end up tomorrow: for example, if we water dry soil, it becomes normal with probability 0.9.

> MDP (марковский процесс принятия решений) — модель, где мы шаг за шагом выбираем действия, а результат немного случаен. «Марковский» значит: завтрашнее состояние зависит только от сегодняшнего состояния и действия, а не от всей истории. Состояния: Dry (сухо) и Normal (норма). Действия: Water (полить) и Wait (ждать). Награды — что получаем сразу: полить сухую +6 (растение спасено минус цена воды), ждать на сухой −10 (растение страдает), полить нормальную −4 (перелив), ждать на нормальной +5 (всё хорошо, вода сэкономлена). Переходы — где окажемся завтра: полили сухую → с вероятностью 0.9 станет нормальной; ждём на сухой → останется сухой (1.0); ждём на нормальной → с вероятностью 0.3 высохнет.

### 6. What does γ = 0.9 mean? Why not 1?

**Say:** γ is the discount. It means a reward tomorrow is worth 90% of the same reward today. The future matters, but a bit less than now. With γ = 1 our plant lives forever, so the total reward can grow without limit and the values never settle. With γ below 1 the sum stays finite, so value iteration is guaranteed to stop. Our code even refuses γ = 1.

> γ (гамма) — коэффициент дисконтирования: награда завтра стоит 90% от такой же награды сегодня. Будущее важно, но чуть меньше настоящего. Если γ = 1, а процесс бесконечный, сумма наград может расти бесконечно и значения никогда не устоятся. При γ < 1 сумма конечна, и алгоритм гарантированно сходится. В коде γ ≥ 1 вызывает ошибку (`greenhouse/mdp.py`, строки 12–13).

### 7. What is a policy?

**Say:** A policy is a simple rule: in each state, which action to take. Our policy is: if the soil is Dry, Water. If the soil is Normal, Wait.

> Policy (политика) — это правило «в каком состоянии какое действие делать». У нас: Dry → Water, Normal → Wait.

### 8. What is value iteration?

**Say:** We start by knowing nothing: every value is 0. Then we repeat one update many times: for each state and action, value = reward now + 0.9 × what we expect tomorrow. Each state keeps the best action's number. After round 1 the values are 6 for Dry and 5 for Normal. After round 2 they are 10.59 and 9.77, and so on, until they stop changing.

> Value iteration (итерация по ценностям): начинаем с нулей. Потом много раз повторяем одно обновление (уравнение Беллмана): Q(s,a) = награда сейчас + 0.9 · ожидаемая ценность завтра. Для каждого состояния берём лучшее действие. После 1-й итерации V(Dry) = 6, V(Normal) = 5. На 2-й: Q(Dry,Water) = 6 + 0.9·(0.1·6 + 0.9·5) = 10.59; Q(Dry,Wait) = −4.6; Q(Normal,Water) = 0.5; Q(Normal,Wait) = 9.77. И так до сходимости.

### 9. Why does value iteration stop? How many iterations?

**Say:** It stops when the values change by less than one millionth (1e-6) in one round. For us that takes 148 iterations. It must stop because γ is below 1. Every round the remaining error shrinks to at most 90% of what it was, so it gets smaller and smaller. We also have a safety limit of 1000 rounds.

> Останавливается, когда за одну итерацию значения меняются меньше чем на 1e-6 (одна миллионная). У нас это 148 итераций. Сходимость гарантирована, потому что γ < 1: каждая итерация уменьшает ошибку минимум до 90% от прежней, ошибка тает. Есть страховка — максимум 1000 итераций. Итог: V*(Dry) = 53.1356, V*(Normal) = 52.2881.

### 10. What are the final Q-values?

**Say:** For dry soil, Water is worth 53.14 and Wait is worth 37.82, so Water wins. For normal soil, Water is worth 43.06 and Wait is worth 52.29, so Wait wins. That is where the policy comes from. Q(s, a) is the total reward we expect if we do action a now and then act in the best way. V(s) is the Q of the best action.

> Q*(Dry,Water) = 53.1356, Q*(Dry,Wait) = 37.8220 → на сухой поливать. Q*(Normal,Water) = 43.0593, Q*(Normal,Wait) = 52.2881 → на нормальной ждать. Q — это «сколько всего хорошего получим, если сейчас сделаем это действие, а дальше будем действовать лучшим образом». V(s) — это Q лучшего действия в состоянии s.

### 11. Why do you weigh the Q-values by P(Dry)?

**Say:** Because we never know the true state for sure. We only know we are 66% sure it is dry. So for each action we mix the two cases: score = 66% × value if dry + 34% × value if normal. Water gets about 49.7, Wait gets about 42.8, so we water.

> Потому что мы не знаем точно, сухо или нет — знаем только вероятность 66%. Поэтому для каждого действия смешиваем два случая: Score(a) = P(Dry)·Q*(Dry,a) + (1 − P(Dry))·Q*(Normal,a). Water: 0.6585·53.14 + 0.3415·43.06 ≈ 49.7. Wait: 0.6585·37.82 + 0.3415·52.29 = 42.76. Water больше → поливаем.

### 12. What is the limitation of this weighing?

**Say:** It is a simplification called QMDP. It assumes that after this step we will know the true state, so it never plans to "check the sensor again". A full POMDP would plan with uncertainty at every step. Our model has no "check again" action anyway, so for two states and two actions QMDP is a reasonable approximation. The full POMDP is future work.

> Это упрощение QMDP: оно предполагает, что после этого шага мы узнаем точное состояние, поэтому никогда не планирует «проверить датчик ещё раз». Полноценный POMDP учитывает неуверенность на каждом шаге. В нашей модели и так нет действия «проверить ещё раз», поэтому для 2 состояний и 2 действий QMDP — разумное приближение. POMDP — в планах на будущее. Одной фразой: «QMDP assumes the uncertainty disappears after one step; a POMDP does not.»

### 13. Where does the 38% threshold come from?

**Say:** It is the point where Water and Wait have the same score. If the soil is dry, watering gains 53.14 − 37.82 = 15.31. If it is normal, watering loses 52.29 − 43.06 = 9.23. We water when b × 15.31 is bigger than (1 − b) × 9.23. That gives b > 9.23 / (15.31 + 9.23) = 0.376, about 38%.

> Это точка, где у Water и Wait одинаковый счёт. Если сухо — полив выигрывает 53.14 − 37.82 = 15.31. Если норма — полив проигрывает 52.29 − 43.06 = 9.23. Поливаем, когда b·15.31 > (1 − b)·9.23, то есть b > 9.23 / 24.54 = 0.376 ≈ 38%. На сайте это точка пересечения двух линий на графике. Фраза: «We water when we are more than 38% sure the soil is dry.»

```
b · 15.31  >  (1 − b) · 9.23
b  >  9.23 / (15.31 + 9.23)  =  0.376
```

### 14. Why hill climbing and not A* or BFS?

**Say:** A* and BFS find a path on a map from a start to a goal. We have no map and no goal state. We only have "which dose makes the plant healthier", and neighbouring doses give similar results. That is a "find the best setting" problem, and hill climbing is the simplest tool for it. Like turning the music volume up or down until it sounds best. To be honest, with 5 doses we could just check all of them. We use hill climbing because the topic asks for it, and because it still works when there are thousands of settings and checking each one is expensive.

> A* и BFS ищут путь по карте от старта до цели. У нас нет карты и нет цели — есть только вопрос «при какой дозе растению лучше», и соседние дозы дают похожий результат. Это задача «подобрать лучшую настройку» (оптимизация), и hill climbing — самый простой инструмент. Как подбирать громкость музыки: чуть громче, чуть тише, пока не станет лучше всего. Если спросят «почему не перебрать все 5?»: честно — при 5 дозах можно и перебрать. Hill climbing требует тема, и он работает, когда настроек тысячи и проверять каждую дорого.

### 15. How does your hill climbing work, step by step?

**Say:** We start at 10 ml, score 55. We look at the neighbours, one dose up and one dose down, and move to the better one only if it is strictly better than where we are. 20 ml gives 72, so we move. From 20, the neighbour 30 ml gives 88, so we move. From 30, the neighbours are 72 and 80, both worse, so we stop. Best dose 30 ml, score 88, in 2 steps.

> Старт 10 мл, оценка 55. Смотрим соседей (±1 доза; у 10 мл сосед только один) и переходим к лучшему, только если он строго лучше. 20 мл → 72, идём. Из 20: 30 мл → 88, идём. Из 30: соседи 72 и 80 хуже — стоп. Лучшая доза 30 мл, оценка 88, 2 шага. С любого старта на этой таблице получается 30 мл.

### 16. What is a local maximum? Show it.

**Say:** A local maximum is a small hill: every neighbour is worse, but somewhere else there is a higher hill. With the tricky plant the scores are 60, 70, 65, 85, 75. From 10 ml we climb to 20 ml with score 70, and both neighbours are worse, so we stop. But the real best is 40 ml with score 85. It is like climbing in fog and stopping on a small hill.

> Локальный максимум — маленький холм: все соседи хуже, но где-то есть холм выше. С «tricky plant» оценки: 60, 70, 65, 85, 75. Из 10 мл поднимаемся на 20 мл (70), соседи 60 и 65 хуже — стоп. А настоящий лучший — 40 мл (85). Как будто лезем в гору в тумане и останавливаемся на маленьком холме.

### 17. How do you fix it?

**Say:** With restarts: we climb again from other starting doses and keep the best top. To be honest, ours is not random: with only 5 doses it is cheap to start from every one of them. Starts at 10 and 20 stop at 20 ml. Starts at 30, 40 and 50 stop at 40 ml. The best of all runs is 40 ml, score 85. With thousands of doses we would pick random starts instead.

> Исправление — перезапуски: лезем заново с других стартовых доз и берём лучшую вершину. Честно: у нас не случайные старты — при 5 дозах дёшево стартовать с каждой. Из 10 и 20 застреваем на 20 мл, из 30, 40 и 50 приходим к 40 мл. Лучший результат — 40 мл, 85. При тысячах доз брали бы случайные старты. На сайте это галочка «Try every start» в блоке «Details for the teacher».

### 18. Where did all these numbers come from?

**Say:** They are hypothetical assumptions, and the course allows that. They are all in one file, `greenhouse/config.py`, marked as assumptions. In a real greenhouse we would learn them from sensor logs: for example, count how often the sensor alerts when the soil is really dry.

> Это допущения (hypothetical), методичка это разрешает. Все они в одном файле `greenhouse/config.py` с пометкой «assumption». В реальной теплице мы взяли бы их из данных: например, посчитали бы по логам, как часто датчик срабатывает на действительно сухой почве.

### 19. Is the decision sensitive to these assumptions?

**Say:** Yes, and our experiment shows it. With the usual 30% prior, we water after an alert even with a 40% false-alarm rate. But if dry soil is rare, 10%, and false alarms are 20%, we are only 33% sure after an alert, which is below 38%, so we wait. A noisy sensor plus rare dryness can mean "do not trust the alarm".

> Да, и эксперимент 1 это показывает. С prior 30% после тревоги поливаем даже при 40% ложных тревог (P(Dry) = 0.49). Но если сухость редкая (10%) и ложных тревог 20%, уверенность всего 33% — ниже 38%, значит ждём. Шумный датчик плюс редкая сухость — повод не доверять тревоге.

### 20. How did you test it? How many tests?

**Say:** We have 41 automated tests with pytest, and all of them pass. They check that the code gives the same numbers we calculated by hand. For Bayes, 66% and 5%. For the MDP, the values after rounds 1 and 2, the final values, the policy, the 38% threshold, and no threshold when all rewards are equal. For hill climbing, the path 10 → 20 → 30 and the tricky mode. They also check the full chain and that the API rejects bad input with a clear error.

> 41 автотест на pytest, все зелёные: Bayes — 7, MDP — 9, hill climbing — 11, pipeline — 5, API — 9. Проверяют, что код выдаёт ровно те числа, что посчитаны вручную (66% и 5%; V₁ и Q на 2-й итерации; V*, Q*, policy, порог 38%, при равных наградах порога нет; путь 10 → 20 → 30, tricky mode и рестарты), что вся цепочка даёт «Water 30 ml» / «Wait», и что API на неправильный ввод (вероятность > 1, переходы не в сумме 1) отвечает ошибкой 422 с понятным сообщением. Запуск: `make test`.

### 21. What would you test next?

**Say:** Next I would test against real sensor data, not only hand-made numbers. I would add tests that run many random inputs and check simple rules, for example that a probability always stays between 0 and 1. And I would add a browser test that clicks through the website.

> Дальше: тесты на реальных данных датчика, а не только на ручных числах; тесты со множеством случайных входов, проверяющие простые правила (например, вероятность всегда от 0 до 1); тест сайта в браузере, который сам прокликивает интерфейс.

### 22. What did AI help with, and what did you do yourself?

**Say:** I used Claude Code as an assistant. It generated most of the code, the website and the drafts of the documents. I chose the topic, set the requirements and the numbers, checked the key results by hand, ran the tests, and made sure I understand every algorithm well enough to explain it today. The full declaration is in `docs/ai-usage-declaration.md`.

> Использовал Claude Code как помощника: он сгенерировал большую часть кода, сайт и черновики документов. Я выбрал тему, задал требования и числа, вручную перепроверил ключевые результаты, запускал тесты и разобрался в каждом алгоритме, чтобы объяснить его на защите. Полная декларация — `docs/ai-usage-declaration.md`. Говори честно и своими словами; если спросят про конкретное место — открой код и объясни (см. вопрос 24).

### 23. What would you improve? How could this become a real product?

**Say:** First, a real soil sensor on an ESP32 board instead of the simulated reading. Second, learn the probabilities and the health scores from logs instead of assuming them. Third, a full POMDP, so the assistant can also decide to "check again" before acting. Fourth, several plants, each with its own model and its own best dose.

> Улучшения: 1) настоящий датчик влажности на плате ESP32 вместо симуляции; 2) учить вероятности и оценки здоровья по логам, а не задавать вручную; 3) полноценный POMDP, чтобы помощник мог решить «проверить ещё раз»; 4) несколько растений, у каждого своя модель и своя доза.

### 24. Show me in the code where it happens.

**Say:** Open the file and point at the line. Use this table.

| What | File | Lines |
|---|---|---|
| Bayes: likelihood for alert / no alert | `greenhouse/bayes.py` | 31–34 |
| Bayes: evidence P(observation) | `greenhouse/bayes.py` | 38 |
| Bayes: posterior, Bayes rule | `greenhouse/bayes.py` | 42 |
| Bellman update `q_value` | `greenhouse/mdp.py` | 24–27 |
| Value iteration loop | `greenhouse/mdp.py` | 38–45 |
| Stop when change < 1e-6 | `greenhouse/mdp.py` | 44–45 |
| γ must be below 1 | `greenhouse/mdp.py` | 12–13 |
| Policy (best action per state) | `greenhouse/mdp.py` | 49 |
| QMDP `decide_under_belief`: scores | `greenhouse/mdp.py` | 65–72 |
| 38% threshold (none if the lines never cross) | `greenhouse/mdp.py` | 75–78 |
| Hill climbing step (look at neighbours, move if strictly better) | `greenhouse/hill_climbing.py` | 33–43 |
| Restarts from every dose | `greenhouse/hill_climbing.py` | 57–64 |
| Chain: Bayes → MDP | `greenhouse/pipeline.py` | 31–36 |
| Chain: dose and final advice | `greenhouse/pipeline.py` | 39–48 |
| All assumed numbers | `greenhouse/config.py` | 8–42 |

> Открой файл и покажи строку. Примеры фраз: «Here, on line 42, we divide the joint probability by the evidence. That is Bayes rule.» (строка 42: делим на P(наблюдения) — это правило Байеса). «Line 27 is the Bellman update: reward now plus gamma times what we expect later.» (награда сейчас + γ · ожидаемое потом). «Line 37: we move only if the neighbour is strictly better.» (идём, только если сосед строго лучше).

### 25. What is the input and output of your system?

**Say:** The input is one sensor reading, alert or no alert, plus the assumed numbers. The output has three parts, as the topic asks: the dry-soil probability, the watering decision, and the best water dose. For example: 66%, Water, 30 ml, which becomes "Water 30 ml now."

> Вход — одно показание датчика (alert / no alert) и заданные числа. Выход — три вещи, как требует тема 04: вероятность сухой почвы, решение о поливе и лучшая доза. Пример: 66%, Water, 30 мл → «Water 30 ml now.»

---

## If you blank out

| Say (EN) | По-русски |
|---|---|
| "Let me show it on the website, it is easier to see." | «Давайте покажу на сайте, так нагляднее». Открой сайт, нажми «Yes, it beeped» / «No, it was quiet», покажи три карточки «How it thinks», открой «Details for the teacher» и читай лог «What the code did» вслух. |
| "Let me go back to the chain: Bayes gives the belief, the MDP gives the action, hill climbing gives the dose." | «Вернусь к цепочке: Байес даёт уверенность, MDP — действие, hill climbing — дозу». |
| "Good question. In simple words, it is like…" and use one of the three one-liners. | «Хороший вопрос. Простыми словами, это как…» и одна из трёх фраз (громкость музыки, датчик, который иногда врёт, «сейчас плюс потом»). |

---

## If the demo fails

1. **Live site does not open.** Run it locally, it works offline:
   ```
   make dev
   ```
   Then open http://localhost:8000. If `make` is not available: `.venv/bin/python -m uvicorn app:app --port 8000`.
2. **The website does not work at all.** Show the console version, it prints every step:
   ```
   .venv/bin/python -m greenhouse.cli
   .venv/bin/python -m greenhouse.cli no_alert
   .venv/bin/python -m greenhouse.cli --tricky --restarts
   ```
3. **Someone asks "does it really work?"** Run the tests: `make test`. Expected: `41 passed`.
4. **Say calmly:** "The live site is not responding, so I will run the same code locally."

> Если сайт не открылся — `make dev` и открыть http://localhost:8000 (работает без интернета). Если не работает вообще — консольная версия `.venv/bin/python -m greenhouse.cli` (с `no_alert`, `--tricky --restarts`). Если сомневаются — `make test`, должно быть `41 passed`. Говори спокойно: «Сайт не отвечает, запущу тот же код локально».
