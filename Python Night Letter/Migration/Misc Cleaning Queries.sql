UPDATE shift_letter_dump 
SET Quality = REPLACE(Quality, "?", "'")
WHERE Quality like "%?%" and not "%? ";

UPDATE shift_letter_dump 
SET Cost = REPLACE(Cost, 'Parts:', '');

UPDATE shift_letter_dump
SET Attachments = REPLACE(Attachments, ';', CHAR(10));





UPDATE shift_letter_dump 
SET '4D'= NULL
WHERE '4D' like '';

UPDATE shift_letter_dump 
SET Top_X_Main = NULL
WHERE Top_X_Main like '';

UPDATE shift_letter_dump 
SET Top_X_Subs = NULL
WHERE Top_X_Subs like '';

UPDATE shift_letter_dump 
SET Cost = NULL
WHERE Cost like '';

UPDATE shift_letter_dump 
SET Top_X = NULL
WHERE Top_X like '';

UPDATE shift_letter_dump 
SET Delivery_ = NULL
WHERE Delivery_ like '';

UPDATE shift_letter_dump 
SET Repairs_Complete = NULL
WHERE Repairs_Complete like '';

UPDATE shift_letter_dump 
SET Attachments = NULL
WHERE Attachments like '';

UPDATE shift_letter_dump 
SET Equip_Failure = NULL
WHERE Equip_Failure like '';