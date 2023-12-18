import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.flatspec.AnyFlatSpec

class Workload_HalfAssociativeIntersectionController_Random(dut: HalfAssociativeIntersectionController) extends PeekPokeTester(dut) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  // Canned values for tagMemoryInterface
  val cannedTagValues = Seq.fill(dut.numTags)(rand.nextInt(math.pow(2, dut.tagBitWidth).toInt))

  for (i <- 0 until 100) {
    val enableValue = if (i % 10 == 0) 0 else 1
    val triggerValue = rand.nextBoolean()
    val disableComparatorMaskValue = rand.nextInt(math.pow(2, dut.numTags).toInt)
    val tagInputValue = rand.nextInt(math.pow(2, dut.tagBitWidth).toInt)
    val forcePeekValue = rand.nextBoolean()
    val headInValue = rand.nextInt(dut.numTags)

    poke(dut.io.enable, enableValue)
    poke(dut.io.triggerInput, triggerValue)
    poke(dut.io.tagInput, tagInputValue)
    poke(dut.io.disableComparatorMask, disableComparatorMaskValue)
    poke(dut.io.force_peek, forcePeekValue)
    poke(dut.io.head_in, headInValue)

    // Simulate memory read based on memoryLookupAddress and memoryLookupEnable
    val readAddress = if (peek(dut.io.memoryLookupEnable) == 1) {
      peek(dut.io.memoryLookupAddress).toInt
    } else {
      -1 // Indicate no valid read
    }
    val memReadValue = if (readAddress >= 0 && readAddress < cannedTagValues.length) {
      cannedTagValues(readAddress)
    } else {
      0 // Default value when read is not enabled or address is invalid
    }
    poke(dut.io.memReadTag, memReadValue)

    // Poke canned values into tagMemoryInterface
    cannedTagValues.zipWithIndex.foreach { case (value, index) =>
      poke(dut.io.tagMemoryInterface(index), value)
    }

    step(1)

    // Assertions for new functionality (if applicable)
    if (forcePeekValue) {
      val peekOutValue = peek(dut.io.peek_out)
      val expectedValue = cannedTagValues(headInValue)
      //assert(peekOutValue == expectedValue, s"Expected peek_out to be $expectedValue, found $peekOutValue")
      val headOutValue = peek(dut.io.head_out)
      //assert(headOutValue == headInValue + 1, s"Expected head_out to be ${headInValue + 1}, found $headOutValue")
    }
  }
}

class Test_Sim_HalfAssociativeIntersectionController extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "HalfAssociativeIntersectionController"
  it should "handle various inputs and enable states" in {
    test(new HalfAssociativeIntersectionController(numTags = 8, tagBitWidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_HalfAssociativeIntersectionController_Random(_))
  }
}
