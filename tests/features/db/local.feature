Feature: Managing local files
    In order to have some music in database
    As a music lover
    I want to get them added to the database

    Scenario: Add files to database
        Given I have some files in "data" directory
        And I add "System Volume Information" pattern
        And I have an empty database
        When I scan the directory for files
        Then they should get added to the database

    Scenario: Add some more files to database
        # Given I have existing database from previous scenario
        When I add some more files to the directory
        And I scan the directory for files again
        Then they should get added to the database

    Scenario: Rename an file
        # Given I have existing database from previous scenarios
        When I rename file "clockwork_test.mp3" to "sweet_hommie.mp3"
        And I scan the directory for files again
        Then they should be updated in the database

    Scenario: Change file tag without changing it's name # (*1)
        # Given I have existing database from previous scenarios
        When I change <tag> tag for file "second_test.flac"
        And I scan the directory for files again
        Then they should be updated in the database

        Examples:
            | tag         |
            | artist      |
            | date        |
            | album       |
            | tracknumber |
            | title       |

    Scenario: Remove a file # (*2)
        # Given I have existing database from previous scenarios
        When I remove file "sweet_hommie.mp3"
        And I scan the directory for files again
        Then it should be removed from the database

    Scenario: Add another separate directory to the database
        Given I have some files in "data2" directory, too
        When I scan the directory for files
        Then they should get added to the database

    Scenario: Disable ignore pattern
        When I disable "System Volume Information" pattern
        And I scan the directory for files again
        Then they should get added to the database

    Scenario: Enable ignore pattern again
        When I enable "System Volume Information" pattern
        And I scan the directory for files again
        Then it should be removed from the database

    Scenario: Remove ignore pattern completely
        When I remove "System Volume Information" pattern
        And I scan the directory for files again
        Then they should get added to the database

    Scenario: Remove first directory
        When I remove the "data" directory
        And I scan the directory for files again
        Then it should be removed from the database

    Scenario: Disable remaining directory
        When I disable the "data2" directory
        And I scan the directory for files again
        Then it should be removed from the database

    Scenario: Enable directory again
        When I enable the "data2" directory again
        And I scan the directory for files agan
        Then they should get added to the database

# *1: It is actualy handled by exchanging two previously prepared files
# *2: It actualy is moved away to temp dir, so we can restore it at the end
