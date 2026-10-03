# Brand battery across languages: translator notes

Machine translations (2026-10-03). Points flagged for native review, per language. The translators also wrote a
Recommend prompt per category; the battery kept only Name (the census question), so the Recommend notes are moot.

## zh

# zh (Simplified, mainland) notes
Templates: name = "说出一{量词}{X}。只回复名称。"; recommend = "能推荐一{量词}{X}吗？". Measure word: 家 for companies/chains/banks, 款 for apps/software/console, 个 elsewhere.
- ai_assistant / ai_company: used native 人工智能 (人工智能助手, 人工智能公司). Natives often type "AI助手"/"AI公司"; reviewer may prefer that.
- credit_card: 信用卡公司. In China cards are issued by banks, so models may answer a bank or a network (银联). No better native term.
- social_network: 社交平台 (more natural than 社交网络 today).
- streaming: 流媒体平台 (could read video-first; matches English ambiguity).
- payment_app / messaging_app / ride_hailing: 支付软件 / 聊天软件 / 打车软件 (colloquial mainland; 应用 more formal). 打车 leans taxi, but is the standard term for ride-hailing apps.
- mobile_carrier: 手机运营商 (运营商 alone is what people say; 手机 added for clarity).
- sneaker: 球鞋品牌 (运动鞋 would overlap sports_brand/running_shoe).
- hotel: 连锁酒店 (chain, not 酒店集团).
- video_game: 游戏主机 (console; excludes PC/mobile).

## zht

# zht (Traditional, Taiwan) notes
Templates: name = "說出一{量詞}{X}。只要回覆名稱就好。"; recommend = "可以推薦一{量詞}{X}嗎？".
- Taiwan vocabulary used: 速食, 筆電, 智慧型手機, 搜尋引擎, 社群平台, 串流平台, 雲端, 專案管理, 通訊軟體, 飯店, 精品, 保養品, 電信公司, 慢跑鞋, 電動車.
- ai_assistant / ai_company: 人工智慧助理 / 人工智慧公司; Taiwanese users often type "AI助理".
- payment_app / ride_hailing: 支付應用程式 / 叫車應用程式. Taiwan usage is overwhelmingly "App" in Latin (叫車App, 支付App); native form chosen per rules, reads slightly formal.
- luxury: 精品品牌 is the natural Taiwan term (奢侈品 sounds mainland/negative).
- mobile_carrier: 電信公司 (covers carriers; also fixed-line telcos, but in Taiwan they are the same companies).
- credit_card: 信用卡公司 (cards issued by banks; same caveat as zh).

## es

# es notes
Templates: "Dime {X}. Responde solo con el nombre." / "¿Me puedes recomendar {X}?" ("Dime" chosen over "Nombra" as more natural in chat).
Regional vocabulary split; neutral choice made:
- laptop: "laptops" (LatAm; Spain says "portátiles").
- car_brand / ev: "autos" (coches in Spain, carros in parts of LatAm).
- sneaker / running_shoe: "zapatillas" (Mexico says "tenis").
- smartphone: "smartphones" (avoids móvil vs celular).
- mobile_carrier: "compañía de telefonía móvil" ("móvil" is Spain-leaning; LatAm "celular").
- ride_hailing: no settled native term; "app de transporte privado con conductor". Reviewer check.
- snack_brand: "snacks" (botanas / aperitivos are regional).
- news_outlet: "medio de noticias" (alt: "medio de comunicación", which is broader).

## pt

# pt-BR notes
Templates: "Cite {X}. Responda só com o nome." / "Você pode me recomendar {X}?"
- snack_brand: "salgadinhos" (savory bias; "snacks" also used, "petiscos" broader). Reviewer check.
- skincare: loanword "skincare" (what BR speakers say; alt "cuidados com a pele").
- credit_card: "empresa de cartão de crédito" may be read as bandeira (network) or emissor (issuer); left ambiguous like the English.
- video_game: "console de videogame" (BR masculine "console"; "um videogame" alone also means console).
- ride_hailing: "app de transporte" (standard BR term; alt "app de corrida").
- news_outlet: "veículo de notícias" (alt "veículo de imprensa").

## fr

# fr notes
Templates: "Cite {X}. Réponds uniquement par le nom." / "Tu peux me recommander {X} ?" (space before "?" per French typography; casual typing often drops it).
- ride_hailing: "appli de VTC" (France-standard; Quebec/Belgium may not use VTC). Reviewer check.
- credit_card: "société de cartes de crédit" (France says "carte bancaire"; kept "crédit" for meaning).
- toy_brand: "fabricant de jouets" (more natural than "entreprise de jouets").
- running_shoe: "chaussures de running" (common usage over "de course").
- sneaker: "baskets" (France; "espadrilles" in Quebec).
- snack_brand: loanword "snacks".

## de

# de notes
Frame: "Nenne X. Antworte nur mit dem Namen." / "Kannst du mir X empfehlen?" (du).
- soda: "Limonadenmarke". In German, Limonade legally/colloquially covers cola and other sweet sodas, but some readers hear "lemonade". Alt: "Softdrink-Marke".
- cereal: "Marke für Frühstücksflocken" (native; "Cerealien" is the loanword alt).
- fashion: "Kleidungsmarke" (exact); "Modemarke" is more common but broader (accessories).
- news_outlet: "Nachrichtenmedium" (covers print/TV/online). "Nachrichtenportal" would bias to online.
- ride_hailing: "Fahrdienst-App" (no settled native term; could read as taxi app).
- credit_card: "Kreditkartenanbieter" (covers networks and issuers).

## it

# it notes
Templates: "Dimmi {X}. Rispondi solo con il nome." / "Mi puoi consigliare {X}?"
- ride_hailing: no native term in common use; "app di auto con conducente" (NCC concept). Reviewer check.
- soda: "bibite gassate" (plain "bibite" includes non-carbonated drinks).
- social_network: "social network" (loanword is the usual term).
- browser, sneaker, snack: loanwords, as commonly used.
- ai_assistant: "assistente IA" ("assistente AI" is also very common).
- skincare: "prodotti per la cura della pelle" (loanword "skincare" also common).

## ru

# ru notes
Frame: "Назови X. Ответь только названием." / "Можешь посоветовать X?" (ты). Cyrillic only (AI = "ИИ").
- sneaker vs running_shoe: Russian "кроссовки" covers both sneakers and athletic shoes, so sneaker = "марку кроссовок", running_shoe = "марку беговых кроссовок"; the two categories overlap more than in English.
- credit_card: "компанию, которая выпускает кредитные карты" (issuer; likely to elicit banks).
- ride_hailing: "приложение для заказа такси" - in Russian usage ride-hailing is taxi-ordering; no neutral native term.
- news_outlet: "новостное издание" (can lean print/online publication; "СМИ" alt).
- "марку" used for product brands; "бренд" only for luxury ("люксовый бренд") and the generic brand category.

## pl

# pl notes
Frame: "Podaj X. Odpowiedz samą nazwą." / "Możesz mi polecić X?" (ty). "Podaj" chosen over "Wymień" (which implies listing several).
- credit_card: "wydawcę kart kredytowych" (issuer). In Poland cards are issued by banks, so this may pull bank names rather than Visa/Mastercard ("organizacja płatnicza").
- news_outlet: "serwis informacyjny" leans online/TV news service; no neat native "outlet" term.
- social_network: "portal społecznościowy" (most common colloquial term).
- ai_assistant / ai_company: "AI" loanword (more common than "SI"); ai_company = "firmę z branży AI".
- sneaker: "sneakersów" (loanword is what people say; "trampki" is narrower).
- camera: "aparatów fotograficznych" (still camera, avoids video "kamera").
- brand / company: bare "markę" / "firmę" reads a bit terse; kept literal.

## ar

# ar notes
- Templates: "اذكر X. أجب بالاسم فقط." / "هل يمكنك أن تقترح عليّ X؟" (MSA; X is in the accusative, so tanween alif on bank "بنكًا", ecommerce "متجرًا إلكترونيًا", ride_hailing "تطبيقًا").
- brand = "علامة تجارية" throughout. Everyday speech often uses "ماركة", but that is less neutral MSA.
- ride_hailing: no settled MSA term. Chose "تطبيقًا لطلب سيارات الأجرة" ("an app for ordering taxis"). This may nudge answers toward taxi apps.
- social_network: "منصة تواصل اجتماعي" (the usual phrase) rather than the literal "شبكة".
- mobile_carrier: "شركة اتصالات للهاتف المحمول"; news_outlet: "مؤسسة إخبارية"; toy_brand: "شركة ألعاب أطفال" ("ألعاب" alone could read as games).
- sneaker "الأحذية الرياضية" vs running_shoe "أحذية الجري": "athletic shoes" is the closest common term for sneakers.

## fa

# fa notes
- Templates: "یک X نام ببر. فقط اسمش را بنویس." / "می‌توانی یک X پیشنهاد کنی؟" (standard written Persian, informal "you", the usual register for a chatbot; ezafe left unwritten).
- supermarket: "فروشگاه زنجیره‌ای" (the Iranian term for a chain store/supermarket) rather than "زنجیره سوپرمارکت".
- ride_hailing: "اپلیکیشن تاکسی اینترنتی". This is the standard Iranian term, but it carries a strong local association.
- messaging_app: "پیام‌رسان" alone (it already means messaging app).
- sneaker: "کفش اسپرت"; running_shoe: "کفش دویدن"; beer: "آبجو".

## tr

# tr notes
Frame: "Bir X söyle. Sadece adını yaz." / "Bir X önerebilir misin?" (sen).
- streaming: "dijital yayın platformu" (common Turkish term for Netflix-type services; leans video, as English does).
- sneaker: loanword "sneaker markası"; native "spor ayakkabı" would overlap with running_shoe/sports_brand.
- ride_hailing: "araç çağırma uygulaması"; Turks may say "taksi uygulaması", which narrows meaning.
- social_network: "sosyal ağ" (exact); "sosyal medya platformu" is more colloquial.
- news_outlet: "haber kuruluşu" (news organisation); "haber sitesi" would bias to online.
- ai: "yapay zeka" without circumflex (common typed form).

## hi

# hi notes
- Templates: "किसी X का नाम बताएं। जवाब में सिर्फ़ नाम लिखें।" / "क्या आप कोई X सुझा सकते हैं?". These parallel the Urdu. Everyday Hindustani with English loans in Devanagari, as typically typed, not Sanskritised (no "पेय", "प्रतिष्ठान" etc.).
- Nukta is used for loans (सॉफ़्ट, फ़ोन, सिर्फ़, ज़). Some users omit it, but it is standard.
- watch / fashion / toy_brand: "घड़ियों का ब्रांड", "कपड़ों का ब्रांड", "खिलौने बनाने वाली कंपनी".
- ride_hailing: "टैक्सी बुक करने वाला ऐप" (kept parallel with the Urdu "ٹیکسی"; "कैब" is also very common in India).
- news_outlet: "न्यूज़ संस्था"; mobile_carrier: "मोबाइल नेटवर्क कंपनी" (Indian users also say "टेलीकॉम कंपनी").
- soda: "सॉफ़्ट ड्रिंक" (the usual term; "सोडा" means soda water). cereal: "ब्रेकफ़ास्ट सीरियल".

## ur

# ur notes
- Templates: "کسی X کا نام بتائیں۔ جواب میں صرف نام لکھیں۔" / "کیا آپ کوئی X تجویز کر سکتے ہیں؟". These parallel the Hindi word for word (بتائیں/बताएं, لکھیں/लिखें, تجویز/सुझा).
- English loanwords are used in Urdu script where Pakistani users actually say them (برانڈ, چین, ایپ, سافٹ ڈرنک, اسکن کیئر, ...). Hindi uses the same loans.
- watch / fashion / toy_brand use native phrasing: "گھڑیوں کا برانڈ", "کپڑوں کا برانڈ", "کھلونے بنانے والی کمپنی".
- ride_hailing: "ٹیکسی بک کرنے والی ایپ" ("an app for booking taxis"). The loan "رائیڈ ہیلنگ" is not in everyday use.
- news_outlet: "نیوز ادارہ" (Hindi uses "न्यूज़ संस्था"). This was the least settled choice.
- mobile_carrier: "موبائل نیٹ ورک کمپنی" (the Pakistani usage).
- soda: "سافٹ ڈرنک" (the usual term; "سوڈا" can mean soda water).
- Gender: ایپ is feminine in Urdu and ऐप is masculine in Hindi. Each follows its language's common usage.

## bn

# bn notes
- Register: polite "apni" forms (বলুন / পারবেন), colloquial একটা. Recommend uses the loanword সাজেস্ট (what people type); সুপারিশ would be more formal.
- soda: কোমল পানীয় (standard in Bangladesh). West Bengal speakers more often say কোল্ড ড্রিংক.
- supermarket: সুপারশপ চেইন. In Bangladesh "সুপার মার্কেট" means a market complex, so সুপারশপ is the right word there. It may read as a Bangladesh-specific term in West Bengal.
- ride_hailing: রাইড শেয়ারিং অ্যাপ (the Bangladesh term for ride-hailing). West Bengal may say ক্যাব বুকিং অ্যাপ.
- social_network: সোশ্যাল মিডিয়া প্ল্যাটফর্ম (common usage). The formal alternative is সামাজিক যোগাযোগমাধ্যম.
- Loanwords kept where they are standard: ব্র্যান্ড, স্ন্যাকস, সিরিয়াল, স্কিনকেয়ার, লাক্সারি, এআই, চেইন. Native terms used: হাতঘড়ি, দৌড়ানোর জুতা, খেলাধুলার পোশাক, সংবাদমাধ্যম, খেলনা.

## ja

# ja notes
Templates: name = "{X}を一つ挙げてください。名前だけで答えてください。"; recommend = "おすすめの{X}を教えてもらえますか？" ("おすすめの" is the idiomatic way to say "recommend"; it does not add "popular/best").
- ai_assistant / ai_company: kept "AI" (AIアシスタント, AI企業). 人工知能アシスタント is not natural Japanese. Latin AI is the standard written form.
- social_network: ソーシャルネットワーク. Natives would usually type "SNS" (Latin), avoided per rules.
- snack_brand: お菓子のブランド (sweets and snacks broadly). スナック菓子 would narrow it to chips.
- toy_brand: おもちゃメーカー (the natural word for a toy company).
- fashion: 洋服のブランド. アパレルブランド is also common and more trade-flavoured.
- luxury: 高級ブランド (ハイブランド is also colloquial).
- cloud: クラウドサービスの事業者 (クラウドプロバイダー is also used).
- mobile_carrier: 携帯電話会社 (キャリア is colloquial but ambiguous).
- video_game: ゲーム機 (covers home and handheld consoles, no PC/mobile).
- Brand vs maker: ブランド used throughout for "brand"; for cars, cameras and laptops Japanese speakers often say メーカー. Kept ブランド for fidelity to English.

## ko

# ko notes
Templates: name = "{X}을/를 하나 말해 주세요. 이름만 답해 주세요."; recommend = "{X} 추천해 줄 수 있어요?" (casual polite 해요체).
- coffee_chain / fast_food: 커피 프랜차이즈 / 패스트푸드 프랜차이즈. Korean says 프랜차이즈 rather than 체인 for these.
- ai_assistant / ai_company: 인공지능 비서 / 인공지능 기업. "AI 어시스턴트" / "AI 기업" are very common in Latin "AI".
- social_network: 소셜 네트워크 (Koreans often type "SNS").
- sneaker: 운동화 브랜드. The native word also covers athletic shoes generally, so it overlaps with running_shoe and sports_brand. 스니커즈 is the loanword alternative.
- luxury: 명품 브랜드 (the standard term).
- supermarket: 슈퍼마켓 체인. Korean chains are often called 대형마트 (hypermarkets), so 대형마트 may be more natural but narrows the meaning.
- ride_hailing: 차량 호출 앱. Colloquially 택시 앱, which is narrower.
- mobile_carrier: 통신사 (standard; strictly "telecom company").
- credit_card: 신용카드사 (usual 카드사).
- video_game: 게임기 (게임 콘솔 is also used).

## id

# id notes
- soda: "merek minuman bersoda". Bare "soda" in Indonesian can suggest soda water.
- smartphone, skincare, laptop, browser, streaming, cloud: English loanwords kept because that is what people say. The formal native terms (ponsel pintar, perawatan kulit, peramban) read stiff.
- ecommerce: "toko online". This may draw individual shops as well as marketplaces. "Situs belanja online" was the alternative.
- ride_hailing: "aplikasi transportasi online", the common generic term. I avoided "ojek online", which is motorbike-specific.
- messaging_app: "aplikasi chat" (colloquial). The formal term would be "aplikasi perpesanan".
- social_network: "media sosial" is what people say. "Jejaring sosial" is the closer literal.

## vi

# vi notes
- ev: "hãng ô tô điện". Bare "xe điện" usually means electric scooters/motorbikes in Vietnam.
- watch: "đồng hồ đeo tay". Bare "đồng hồ" also means clock.
- news_outlet: "cơ quan báo chí" (media organisation). This is slightly formal; "trang tin tức" would narrow it to websites.
- streaming: "dịch vụ phát trực tuyến". People also say "dịch vụ streaming".
- snack_brand: "đồ ăn vặt" is broader than packaged snacks ("snack" in VN often means chips).
- video_game: "máy chơi game" = console.

## sw

# sw notes
- Several tech terms have coined Swahili equivalents that are standard in Tanzania but less used in Kenya, where English loanwords dominate: simu janja (smartphone), kompyuta mpakato (laptop), utiririshaji (streaming), kompyuta ya wingu (cloud), kivinjari (browser). I chose the Swahili terms. A Kenyan reviewer may prefer the loanwords.
- "chain" rendered as "mnyororo wa ..." (coffee_chain, fast_food, hotel, supermarket). This is understood but a bit literal.
- sneaker: "raba" (colloquial for sneakers in both KE and TZ).
- cereal: "kifungua kinywa" (TZ). Kenya says "kiamsha kinywa".
- mobile_carrier: "kampuni ya mtandao wa simu" ("mtandao" is the everyday word for a carrier).
- ride_hailing: "programu ya kuagiza usafiri" (an app to order a ride). There is no settled term.
- video_game: "konsoli ya michezo ya video". The loanword "konsoli" may be unfamiliar.
- AI kept as "AI" rather than "akili bandia".
