Feature: Synchronizing database with internet knowledge
    In order to get in touch with the news
    As a lazy man
    I want to sync my local db with internet ones

    Scenario: Get in sync using one-by-one mode
        Given I have an existing database with some entries
        When I start an internet update for "metal-archives.com" or "musicbrainz.org"
        Then I should get releases from either of them (but never both)

    Scenario: Get in sync using crossed mode
        Given I have an existing database with some entries
        When I start an internet update for "metal-archives.com" and "musicbrainz.org"
        Then I should get releases from both of them (possibly)

    # Scenarios below are not really testing a daily usage, but I need to have
    # it tested somehow anyway and real remote dbs can change in time making
    # our tests fail, so we're just mocking a result here.
    Scenario: Add some entries received from the first remote database
        Given I have an existing database with some entries
        When I add some remote informations from "remote1" to it
        Then The local database should get updated appropriately

    Scenario: Add some entries received from the second remote database
        When I add some remote informations from "remote2" to it
        Then The local database should get updated appropriately

    Scenario: Remove some entries received from the first remote database
        When I remove some remote informations from "remote1" from it
        Then The local database should get updated appropriately

    Scenario: Remove some entries received from the second remote database
        When I remove some remote informations from "remote2" from it
        Then The local database should get updated appropriately
