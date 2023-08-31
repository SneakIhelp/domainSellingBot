# domainSellingBot
2 бота
1 основной 
2 для доменов 


Обсудим для начала второй бот 
Приветствие - описание правил + соглашение с ними 

Базово идет 5 кнопок: 
1 пополнить баланс 
2 профиль 
3 купить домены
4 купить хост
5 мои услуги 

1: все легко и просто - жмем кнопку просит ввести сумму пополнения в $ 
Методы оплат: USDT TRC20, Btc, eth

2: жмешь эту кнопку - получаешь всю необходимую информацию 
1 текущий баланс
2 сумма покупок 
3 текущий процент скидки 
Нужно считать скидку, в зависимости от кол-ва покупок : 
1000$ - 3%
5000$ - 5%
10000$ - 10%

3: тут уже потяжелее система:
После нажатия на эту кнопку, пишет текущую сумму баланса, с учетом скидки предлагает основные доменные зоны и их цену:
.com - 23$
.net - 25$
.org - 23$
И тут еще кнопка «посмотреть другие доменные зоны» 
И кнопками надо все доменные зоны сделать - список с ценами дам попозже 
После выбора доменной зоны пользователю предлагает вписать незвание домена, без доменной зоны 
Он вписывает к примеру airdrop-pepe первоначально выбрав .com зону 
Бот проверяет доступна ли эта доменная зона - если доступна пользователю дается выбор «купить» «отмена» 
Иначе предлагает выбрать другое доменное имя 

После покупки домен будет в 5 пункте 

4: тоже тяжелый пункт, но еще тяжелее 
После нажатия снова пишет текущий баланс, и все цены с учетом скидок  
3 выбора хоста:
1 pq hosting 
2 ddos guard 
3 приват защита от любых атак

1 пункт если нажимает - дает на выбор 4 разных конфигурации хоста, позже покажем

2 пункт - на выбор: 
 1. Общий сервер ddos guard - 12$ домен
 2. Сервер ddos guard для одного домена - 80$
 3. Личный сервер для 50-ти доменов - 350$ 
Объясню позже что куда

3 пункт - 1 домен = 95$. 

Все описания к каждому товару мы сами составим в конфиг файл

После покупки все переносится в 5 пункт 

5: тут уже проще
По нажатию выходят 2 кнопки
1 мои сайты 
2 мои хостинги

По нажатию первой - выходит список доменов и хостов - на каждый можно нажать и редактировать 
Домены - сменить IP привязки
Хостинги - (пишет IP хоста) - показывает текущие домены на хосте + кнопка добавить домен

По визуальной части это все, перейдем к технической 

Www.nicenic.net - здесь мы покупаем домены, под него нужно реализовать API - покупка домена + привязка NS 

Cloud flare - в бота мы будем пополнять аккаунты клауда в txt формате, один аккаунт клауда = 20 доменов максимум 
С Клауд аккаунта  нужно получить NS сервера, и подвязать к нужному домену, затем по API на хост, который укажет пользователь 

По поводу хостов: нужна возможность автоматически создавать папки под домены, и возможность закидывать туда файлы - если это невозможно сделать автоматически, то придумаем что нибудь 

Pq hosting - нужна автомат покупка хоста как только пользователь купил хост, по сути можно и другие сервисы хостов заюзать но вроде этот самый простой 

Ddos guard - по поводу хостов за 80$ - покупать автоматически, по API 
Общие хосты уже надо реализовать под создание папки домена

Личные сервера мы сами будем создавать и грузить 

3 пункт хосты за сотку - это максимальная защита, которая доступна на рынке - подключение через саппорта 

Второй бот готов

Теперь основной - банальный прием заявок в 3 пункта - отправка в админку с приемом/отклонением заявки

По вступлению Надо выдавать каждому по домену бесплатному, пополнять будем через .txt - соответственно нужно реализовать подвязку домена за каждым работником
Дрейнер уже куплен - дрейнер Павла 
Как я предлагаю чтобы все работало: за каждым работником закреплялся домен, а все логи шли в какой-то канал, бот видит домен воркера в сообщении - отправляет это воркеру 
Соответственно все залеты надо фиксировать, потому что бывают боты которые «якобы» залетают, но на деле - нет соответственно нужно реализовать проверку залетело или нет
Теперь поговорим о самом меню бота 

5 пунктов 
 1. Привязать домен 
 2. Профиль
 3. Вывод
 4. Информация
 5. Поддержка 

1: тут по сути все просто, жмешь эту кнопку, вписываешь домен - заявка на привязку отправляется нам мы принимаем / отклоняем + защита от спама нужна, не более 5 доменов за час отправлять
2: в профиле нужно: 
 1. Никнейм воркера 
 2. Сумма его профитов за 24 часа 
 3. Сумма его профитов за все время
 4. Добавить кнопку с реферальной системой - соответственно ее нужно реализовать 5% с профитов 
 5. Его текущие домены
 6. Функцию перевода во второй бот с 5% бонусом 
3: вывод - по нажатию этой кнопки пользователю дает на выбор 2 кнопки - вывести + вывести чистые (комиссия 7%)

4: информацию мы заполним сами по этой кнопке надо сделать текст который мы сами укажем

5: здесь контакты поддержки 

Бот должен работать уверенно, без косяков ведь каждый косяк = - прибыль, по сути все что нужно отписал



из того что готово - в принципе определенные пояснение в коде есть, не работает оплата по USDT в crystal pay (его обязательно использовать для пополенения). Ниже все методы оплаты которые могут быть (но вроде как большая часть не работает вообще). Выглядит ужасно, если честно

{"error":false,"errors":[],"methods":{"CRYSTALPAY":{"name":"CrystalPAY P2P","enabled":true,"extra_commission_percent":0,"minimal_status_level":0,"currency":"RUB","commission_percent":0,"commission":0},"TEST":{"name":"Test","enabled":false,"extra_commission_percent":0,"minimal_status_level":-1,"currency":"RUB","commission_percent":0,"commission":0},"CARDRUBP2P":{"name":"Card RUB P2P","enabled":true,"extra_commission_percent":0,"minimal_status_level":2,"currency":"RUB","commission_percent":2.5,"commission":0},"CARDTRYP2P":{"name":"Card TRY P2P","enabled":true,"extra_commission_percent":0,"minimal_status_level":2,"currency":"TRY","commission_percent":7,"commission":0},"LZTMARKET":{"name":"LZT Market","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"RUB","commission_percent":1,"commission":0},"BITCOIN":{"name":"Bitcoin","enabled":true,"extra_commission_percent":0,"minimal_status_level":0,"currency":"BTC","commission_percent":0,"commission":4.0e-6},"BITCOINCASH":{"name":"Bitcoin Cash","enabled":true,"extra_commission_percent":0,"minimal_status_level":0,"currency":"BCH","commission_percent":0,"commission":0.0003},"DASH":{"name":"Dash","enabled":true,"extra_commission_percent":0,"minimal_status_level":0,"currency":"DASH","commission_percent":0,"commission":0.0006},"DOGECOIN":{"name":"Dogecoin","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"DOGE","commission_percent":0,"commission":0.5},"ETHEREUM":{"name":"Ethereum","enabled":true,"extra_commission_percent":0,"minimal_status_level":0,"currency":"ETH","commission_percent":0,"commission":0.0015},"LITECOIN":{"name":"Litecoin","enabled":true,"extra_commission_percent":0,"minimal_status_level":0,"currency":"LTC","commission_percent":0,"commission":0.0006},"BNBSMARTCHAIN":{"name":"BNB Smart Chain","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"BNB","commission_percent":0,"commission":0.00028},"POLYGON":{"name":"Polygon","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"MATIC","commission_percent":0,"commission":0.025},"TRON":{"name":"Tron","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"TRX","commission_percent":0,"commission":2},"USDCTRC":{"name":"USDC TRC-20","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"USDC","commission_percent":0,"commission":1},"USDTTRC":{"name":"USDT TRC-20","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"USDT","commission_percent":0,"commission":1},"BNBCRYPTOBOT":{"name":"CryptoBot BNB","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"BNB","commission_percent":3,"commission":0},"BTCCRYPTOBOT":{"name":"CryptoBot BTC","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"BTC","commission_percent":3,"commission":0},"ETHCRYPTOBOT":{"name":"CryptoBot ETH","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"ETH","commission_percent":3,"commission":0},"TONCRYPTOBOT":{"name":"CryptoBot TON","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"TON","commission_percent":3,"commission":0},"USDTCRYPTOBOT":{"name":"CryptoBot USDT","enabled":true,"extra_commission_percent":0,"minimal_status_level":1,"currency":"USDT","commission_percent":3,"commission":0}}}

В общем я сделал пока что до API www.nicenic.net, то есть до покупки доменов, там как раз самая жесть, конечно

еще бд сделано на скорую руку, нужно подредактировать чтобы все соответствовало задаче (я быстро накидал, чтобы работало там до доменов)
