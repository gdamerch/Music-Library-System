CREATE TABLE SONG (
    S_SONGID INTEGER NOT NULL,          -- Song's ID
    S_ALBUMID INTEGER NOT NULL,         -- ID of the album the song is in
    S_ARTISTID INTEGER NOT NULL,        -- ID of the artist the song was made by
    S_TITLE VARCHAR(999),               -- Title of the song
    S_GENRE CHAR(99),                   -- Genre of the song
    S_DURATION TIME                     -- Duration of the song
);

CREATE TABLE PLAYLIST ( 
    P_PLAYLISTID INTEGER NOT NULL,      -- Playlist's ID
    P_UID INTEGER NOT NULL,             -- ID of the user who made the playlist
    P_TITLE VARCHAR(999),               -- Title of the playlist
    P_PRIVATE BOOLEAN NOT NULL,         -- Whether the playlist is private or public
    P_CREATIONDATE DATE,                -- Date playlist was made
    P_LENGTH INTEGER NOT NULL           -- Number of songs
);

CREATE TABLE USERS (
    U_UID INTEGER NOT NULL,             -- ID of the user
    U_USERNAME VARCHAR(50) NOT NULL,    -- User's username
    U_EMAIL CHAR(999) NOT NULL,         -- User's email
    U_PASSWORD CHAR(50) NOT NULL        -- User's password
);

CREATE TABLE ALBUM (
    A_ALBUMID INTEGER NOT NULL,         -- ID of the album
    A_ALBUMNAME VARCHAR(999),           -- Name of the album
    A_ARTISTID INTEGER NOT NULL,        -- ID of the artist who made the album
    A_NUMBEROFSONGS INTEGER NOT NULL,   -- Number of songs in album
    A_RELEASEDATE DATE,                 -- Date album was released
    A_DURATION TIME                     -- Duration of the albuim
);

CREATE TABLE ARTIST (
    AR_ARTISTID INTEGER NOT NULL,       -- ID of the artist
    AR_NAME VARCHAR(99) NOT NULL,       -- Name of the artist
    AR_COUNTRY VARCHAR(99) NOT NULL     -- Artist's country of origin
);

CREATE TABLE PLAYLISTSONG (
  PS_PlaylistID INT,                    -- Playlist's ID
  PS_SongID INT                         -- Song's ID
);