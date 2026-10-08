package com.learnsstream;

import com.learnsstream.service.ProblemService;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Fast unit tests that don't need MySQL, so `mvn package` works on any machine.
 * (A full @SpringBootTest would need a running database.)
 */
class LearnStreamBackendApplicationTests {

    private static String normalize(String s) throws Exception {
        Method m = ProblemService.class.getDeclaredMethod("normalize", String.class);
        m.setAccessible(true);
        return (String) m.invoke(null, s);
    }

    @Test
    void outputComparisonIgnoresTrailingWhitespaceAndWindowsNewlines() throws Exception {
        assertEquals(normalize("1 2 3\n4 5\n"), normalize("1 2 3  \r\n4 5\r\n\r\n"));
    }

    @Test
    void outputComparisonKeepsInnerDifferences() throws Exception {
        assertEquals("a\nb", normalize("a\nb\n"));
        assertEquals(false, normalize("a b").equals(normalize("ab")));
    }
}
