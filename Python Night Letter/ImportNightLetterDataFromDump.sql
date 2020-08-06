INSERT INTO NightLetterData
SELECT 
	ID, 
	Date, 
	Crew, 
	Production_Crew, 
	"Start Card Audit CNT", 
	coalesce("4D" || CHAR(10), '') || coalesce(Top_X_Main || CHAR(10), '') || coalesce(Top_X_Subs || CHAR(10), '') || coalesce(Attachments || CHAR(10), ''),
	Safety, 
	coalesce(Delivery_ || CHAR(10), '') || Top_X, 
	Quality, 
	Dimensional_Log, 
	Notifications, 
	Recognition, 
	coalesce(Equip_Failure || CHAR(10), '') || coalesce(Repairs_Complete || CHAR(10), '') || Cost,  
	Door_Log, 
	Follow_Up, 
	Enviromental
FROM shift_letter_dump;