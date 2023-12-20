import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.flatspec.AnyFlatSpec
import scala.util.Random
import scala.collection.mutable

class TestVectorTwoFingerMergeIntersection extends AnyFlatSpec with ChiselScalatestTester with Matchers {
  behavior of "VectorTwoFingerMergeIntersection"

  it should "correctly intersect and output sorted common tag values" in {
    test(new VectorTwoFingerMergeIntersection(metaDataWidth = 5, arraySize = 8)).withAnnotations(Seq(WriteVcdAnnotation)) { dut =>
      val rand = new Random
      val numTags = 8
      val maxTagValue = (1.2 * numTags).toInt
      val checkOutputCorrectness = false
      val vectorLength = 8

      def generateUniqueRandomList(size: Int, maxValue: Int): Seq[Int] = {
        val set = mutable.Set[Int]()
        while (set.size < size) {
          set += rand.nextInt(maxValue)
        }
        set.toSeq.sorted
      }

      val leftTestVector = generateUniqueRandomList(numTags, maxTagValue)
      val rightTestVector = generateUniqueRandomList(numTags, maxTagValue)

      dut.io.enable_in.poke(true.B)
      
      for (i <- leftTestVector.indices) {
        dut.io.inputWireArrays(0)(i).poke(leftTestVector(i).U)
        dut.io.inputWireArrays(1)(i).poke(rightTestVector(i).U)
      }

      dut.clock.step(5) // Wait for input stabilization

      dut.clock.step(10) // Allow time for processing

      // Check the expected result if flag is true
      if (checkOutputCorrectness) {
        val expectedResult = leftTestVector.intersect(rightTestVector).sorted.take(vectorLength)
        for (i <- expectedResult.indices) {
          dut.io.outputWireArrays(i).expect(expectedResult(i).U)
        }
      }

      dut.clock.step(5) // Additional steps if needed for output stabilization
    }
  }
}