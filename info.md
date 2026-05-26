As of now i want a clean workflow that 

when user interact to AI 

if he interacting regrading the injury or any other trauma our model should interact, also it should gain the knowledge about that by asking some questions related and that too user understandable structure and language

After some three to four question itself and also giving severity score after that four questions then if needed just confrim question can be asked after like (two) the it should come to know full picture as soon as possbile. ( Have some quality in this flow)

ones AI gets full picture then the supervisor node will take neccessary actions for that 

- if user has High severity then  doctor finder nearby radius( 4kms) also from the db too and suggest the doctors who are specialized for user issue then user will choose the doctor then send a detailed report to them through email also send report to the user email too.

- if low severity then the conversion itself should give first aid knowledge and some tips also if users conditions itself worse after some convo then it again check severity level then take necessary actions (similar to High sever)

If AI is suggesting any neabry doctors then confrim the location with users before also if user enters any locations manually that also should be considered. give a location example like ( Royapuram, Chennai Tamilnadu) and user enter then search doctor in that specific locations 

suggest min 5 doctors and max 10 doctors only and show them 

constraints: 

Use good enpoints and optimized our porject we been using twoo LLMs (Gmeini and Grok) so use that properly for tasks and also uncessary call should not be made (use wisely) 

dont implement doctors registerarion and user logins etc 

I want the AI workflow should be good so any extra endpoint or anything needed analyse and plan acordingly then implement it