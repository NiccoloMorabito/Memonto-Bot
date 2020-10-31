# Changelog

## [1.2] - 2020-10-31

### Added

- Translation of calendar for expiring date of memonto (now it is available also in Italian)
- New method of memonto creation with only one message that shows the memonto in progress and the field request

### Changed

- Fixed the bug in the clock that led to sending all the notifications one minute before the right time
- Optimization of the code
- Now the memonto is not saved until the creation ends and the confirmation message is sent. In this way, errors during fields insertion do not leave incomplete memontos
- New calendar for expiring date of memonto available: you are now able to change month or year more easily clicking on the button in the lower center
- Memontos in "Delete memonto" section are now summarized with a brand + description text instead of its generated id
- Memontos' messages in "List memontos" section and notifications are now better formatted and ids have been removed; moreover, now there is no more one message for each memonto in listing but all strings are concatenated in one message
- Now in "List memontos" you are asked to choose category only if your memontos have not all the same category
- Notifications of expired memontos or reminders are now collected in one single message for each category

## [1.1.2] - 2020-10-21

### Changed

- For listing memontos, you are now able to select the category of memontos you want to list
- Changed notification texts in order to make them more readable
- New method to insert expiring date and time of a memonto: inline calendar for date, message for time

### Removed

- Little bug in notification for memonto expiration fixed
- Other minor bugs fixed

## [1.1.1] - 2020-10-09

### Added

- Now the discount code of a memonto is formatted in order to automatically copy it when clicking on it
- Added source code link in the INFO section

### Changed

- Changed limit for fields during the creation of a memonto
- Better organization of keyboard for category choice
- Update in changelogs message
- Welcome message



## [1.1] - 2020-10-02

### Added

- Now the help message allows you to select what specific help you need
- Added default reminders for new users: 1h, 8h and 1d

### Changed

- Modified welcome and help messages to clarify how the bot works
- Fixed the bug that maintained the menu keyboard in memonto creation/deletion and reminder addition/remotion.

### Removed

- Removed language choice on first use of the bot. Now the default language of a new user is based on the language he/she has selected on Telegram app (but you can still change your language any time you want)



## [1.0.2] - 2020-09-22

### Added

- Added this wonderful option which allows you to see changelogs
- Added the option to cancel reminder addition during its creation

### Changed

- Bug in the welcome message after language choice fixed
- Changed the button for cancelling the creation of memonto. Now it is an inline button that appears after each request



## [1.0.1] - 2020-09-20

### Changed

- Bug in the category choice for creation memonto fixed