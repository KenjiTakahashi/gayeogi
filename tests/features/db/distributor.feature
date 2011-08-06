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
