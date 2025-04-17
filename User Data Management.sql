-- Create Users Table
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Age INT,
    BirthPlace NVARCHAR(100),
    Height NVARCHAR(10),
    Weight NVARCHAR(10),
    Measurements NVARCHAR(20),
    BodyType NVARCHAR(50),
    ButtockType NVARCHAR(50),
    BreastSize NVARCHAR(50)
);

-- Stored Procedure to Insert User Data
CREATE PROCEDURE InsertUserData
    @Name NVARCHAR(100),
    @Age INT,
    @BirthPlace NVARCHAR(100),
    @Height NVARCHAR(10),
    @Weight NVARCHAR(10),
    @Measurements NVARCHAR(20),
    @BodyType NVARCHAR(50),
    @ButtockType NVARCHAR(50),
    @BreastSize NVARCHAR(50)
AS
BEGIN
    INSERT INTO Users (Name, Age, BirthPlace, Height, Weight, Measurements, BodyType, ButtockType, BreastSize)
    VALUES (@Name, @Age, @BirthPlace, @Height, @Weight, @Measurements, @BodyType, @ButtockType, @BreastSize);
END;

-- Stored Procedure to Fetch All Users
CREATE PROCEDURE FetchAllUsers
AS
BEGIN
    SELECT * FROM Users;
END;

-- Stored Procedure to Fetch User By Name
CREATE PROCEDURE FetchUserByName
    @Name NVARCHAR(100)
AS
BEGIN
    SELECT * FROM Users WHERE Name LIKE '%' + @Name + '%';
END;

-- Stored Procedure to Update User Data
CREATE PROCEDURE UpdateUserData
    @UserID INT,
    @Name NVARCHAR(100),
    @Age INT,
    @BirthPlace NVARCHAR(100),
    @Height NVARCHAR(10),
    @Weight NVARCHAR(10),
    @Measurements NVARCHAR(20),
    @BodyType NVARCHAR(50),
    @ButtockType NVARCHAR(50),
    @BreastSize NVARCHAR(50)
AS
BEGIN
    UPDATE Users
    SET
        Name = @Name,
        Age = @Age,
        BirthPlace = @BirthPlace,
        Height = @Height,
        Weight = @Weight,
        Measurements = @Measurements,
        BodyType = @BodyType,
        ButtockType = @ButtockType,
        BreastSize = @BreastSize
    WHERE UserID = @UserID;
END;

-- Stored Procedure to Delete User by UserID
CREATE PROCEDURE DeleteUserByID
    @UserID INT
AS
BEGIN
    DELETE FROM Users WHERE UserID = @UserID;
END;

-- Stored Procedure to Export Data to CSV
-- This will be done using SQL Server's BCP utility (external process), so we are just outlining the stored procedure.
CREATE PROCEDURE ExportUsersToCSV
    @FilePath NVARCHAR(255)
AS
BEGIN
    -- This needs the SQL Server BCP utility to export data.
    EXEC xp_cmdshell 'bcp "SELECT * FROM Users" queryout ' + @FilePath + ' -c -t, -T -S localhost';
END;
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user'
);
