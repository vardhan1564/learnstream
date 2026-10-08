package com.learnsstream.exception;

/** Thrown when an email can't be sent. Not an ApiException on purpose, so transactions roll back. */
public class EmailSendException extends RuntimeException {

    public EmailSendException(String message) {
        super(message);
    }
}
