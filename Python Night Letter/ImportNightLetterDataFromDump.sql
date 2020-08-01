INSERT INTO NightLetterData
SELECT 
	ID, 
	Date, 
	Crew, 
	Production_Crew, 
	"Start Card Audit CNT", 
	SPL_Attachment || ";" || 4D || ";" || FRACAS_Attachment || ";" || Top_X_Main || ";" || Top_X_Subs || ";" || Attachments, 
	Safety, 
	Delivery_ || "\n" || Top_X, 
	Quality, 
	Dimensional_Log, 
	Notifications, 
	Recognition, 
	Equip_Failure || "\n" || Repairs_Complete || "\n" || Cost,  
	Door_Log, 
	Follow_Up, 
	Enviromental
FROM shift_letter_dump;