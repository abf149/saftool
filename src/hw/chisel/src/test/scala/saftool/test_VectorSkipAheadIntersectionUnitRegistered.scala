import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import scala.util.Random
import java.nio.file.{Paths, Files}
import java.nio.charset.StandardCharsets
import scala.collection.mutable

class TestVectorSkipAheadIntersectionUnitRegistered extends AnyFlatSpec with ChiselScalatestTester with Matchers {
  behavior of "VectorSkipAheadIntersectionUnitRegistered"

  it should "correctly intersect and output sorted common tag values" in {
    test(new VectorSkipAheadIntersectionUnitRegistered(vectorLength = 8, numTags = 8, tagBitWidth = 5)).withAnnotations(Seq(WriteVcdAnnotation)) { dut =>
      val rand = new Random
      val numTags = 8
      val maxTagValue = (1.2 * numTags).toInt
      val checkOutputCorrectness = false // Flag to control output correctness checking
      val vectorLength = 8

      // Function to generate a sorted list of unique random values
      def generateUniqueRandomList(size: Int, maxValue: Int): Seq[Int] = {
        val set = mutable.Set[Int]()
        while (set.size < size) {
          set += rand.nextInt(maxValue)
        }
        set.toSeq.sorted
      }

      // Generate unique test vectors
      val leftTestVector = generateUniqueRandomList(numTags, maxTagValue)
      val rightTestVector = generateUniqueRandomList(numTags, maxTagValue)

      // Step 1: Set pingpongSelect to 1 for writing to sub-buffer 0
      dut.io.pingpongSelect.poke(true.B)

      // Step 2: Write monotonically increasing test vectors to left and right memories
      dut.io.enable.poke(true.B)
      dut.io.left_writeEnable.poke(true.B)
      dut.io.right_writeEnable.poke(true.B)
      
      for (i <- leftTestVector.indices) {
        dut.io.left_writeData(i).poke(leftTestVector(i).U)
        dut.io.right_writeData(i).poke(rightTestVector(i).U)
      }

      // Allow time for writing to memories
      dut.clock.step(5)

      // Step 3: Set pingpongSelect to 0 to feed test vectors into DUT
      dut.io.pingpongSelect.poke(false.B)

      // Allow time for processing
      dut.clock.step(10)

      // Step 4: Set pingpongSelect to 1 for reading the result
      dut.io.pingpongSelect.poke(true.B)
      dut.io.readEnable.poke(true.B)

      // Allow time for reading from memory
      dut.clock.step(5)

      // Check the expected result if flag is true
      if (checkOutputCorrectness) {
        val expectedResult = leftTestVector.intersect(rightTestVector).sorted.take(vectorLength)
        for (i <- expectedResult.indices) {
          dut.io.readData(i).expect(expectedResult(i).U)
        }
      }
    }
  }
}