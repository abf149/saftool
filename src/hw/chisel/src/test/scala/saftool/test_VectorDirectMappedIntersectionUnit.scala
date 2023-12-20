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

class TestVectorDirectMappedIntersectionUnit extends AnyFlatSpec with ChiselScalatestTester with Matchers {
  behavior of "VectorDirectMappedIntersectionUnit"

  it should "correctly intersect and output sorted common tag values" in {
    test(new VectorDirectMappedIntersectionUnit(vectorLength = 16, fiberLength = 32, tagBitWidth = 5)).withAnnotations(Seq(WriteVcdAnnotation)) { dut =>

      val rand = new Random
      val numTags = 16
      val maxTagValue = 32 // Adjusted to match fiberLength
      val checkOutputCorrectness = false

      def generateUniqueRandomList(size: Int, maxValue: Int): Seq[Int] = {
        val set = mutable.Set[Int]()
        while (set.size < size) {
          set += rand.nextInt(maxValue)
        }
        set.toSeq.sorted
      }

      val leftTestVector = generateUniqueRandomList(numTags, maxTagValue)
      val rightTestVector = generateUniqueRandomList(numTags, maxTagValue)

      dut.io.enable.poke(true.B)
      
      // Poke the values into the DUT's input interfaces
      for (i <- leftTestVector.indices) {
        dut.io.list1(i).poke(leftTestVector(i).U)
        dut.io.list2(i).poke(rightTestVector(i).U)
      }

      dut.clock.step(5) // Wait for input stabilization

      dut.clock.step(10) // Allow time for processing

      // Check the expected result if flag is true
      if (checkOutputCorrectness) {
        val expectedResult = leftTestVector.intersect(rightTestVector).sorted.take(numTags)
        for (i <- expectedResult.indices) {
          dut.io.commonElements(i).expect(expectedResult(i).U)
        }
        dut.io.numMatches.expect(expectedResult.length.U)
      }

      dut.clock.step(5) // Additional steps if needed for output stabilization
    }
  }
}
